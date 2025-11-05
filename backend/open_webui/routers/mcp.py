"""
MCP (Model Context Protocol) Router
Provides API endpoints for managing MCP servers, resources, and tools
"""

import logging
import json
import time
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from open_webui.models.users import Users
from open_webui.models.mcp import (
    MCPServers,
    MCPResources,
    MCPTools,
    MCPServerModel,
    MCPServerForm,
    MCPServerUpdateForm,
    MCPResourceModel,
    MCPToolModel,
)
from open_webui.utils.auth import get_current_user, get_admin_user
from open_webui.utils.mcp.client import MCPClient

log = logging.getLogger(__name__)

router = APIRouter()

#####################
# Helper Functions
#####################


async def get_mcp_client_for_server(server: MCPServerModel) -> MCPClient:
    """Create and connect MCP client for a server"""
    client = MCPClient(server_id=server.id)

    try:
        if server.type == "stdio":
            await client.connect_stdio(
                command=server.command,
                args=server.args,
                env=server.env,
            )
        elif server.type == "sse":
            headers = {}
            if server.auth_type == "bearer" and server.auth_config:
                token = server.auth_config.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            await client.connect_sse(url=server.url, headers=headers or None)
        elif server.type == "streamable_http":
            headers = {}
            if server.auth_type == "bearer" and server.auth_config:
                token = server.auth_config.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
            await client.connect_http(url=server.url, headers=headers or None)
        else:
            raise ValueError(f"Unsupported transport type: {server.type}")

        return client
    except Exception as e:
        log.error(f"Failed to connect to MCP server {server.id}: {e}")
        await client.disconnect()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to MCP server: {str(e)}"
        )


def check_server_access(server: MCPServerModel, user: Users) -> bool:
    """Check if user has access to server"""
    return server.user_id == user.id or server.is_global or user.role == "admin"


#####################
# Server Management
#####################


@router.get("/servers", response_model=List[MCPServerModel])
async def get_servers(user: Users = Depends(get_current_user)):
    """Get all MCP servers accessible to the current user"""
    try:
        # Get user's personal servers
        servers = MCPServers.get_servers_by_user_id(user.id)

        # Add global servers
        global_servers = MCPServers.get_global_servers()
        servers.extend(global_servers)

        # Admins see all servers
        if user.role == "admin":
            # Get all servers (including other users' private servers)
            with get_db() as db:
                all_servers = db.query(MCPServer).all()
                server_ids = {s.id for s in servers}
                for server in all_servers:
                    if server.id not in server_ids:
                        servers.append(MCPServerModel.model_validate(server))

        return servers
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}", response_model=MCPServerModel)
async def get_server(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Get a specific MCP server by ID"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    return server


@router.post("/servers", response_model=MCPServerModel)
async def create_server(
    form: MCPServerForm,
    user: Users = Depends(get_current_user)
):
    """Create a new MCP server"""
    try:
        server_id = str(uuid.uuid4())

        # Validate transport-specific fields
        if form.type == "stdio":
            if not form.command:
                raise HTTPException(
                    status_code=400,
                    detail="Command is required for stdio transport"
                )
        elif form.type in ["sse", "streamable_http"]:
            if not form.url:
                raise HTTPException(
                    status_code=400,
                    detail="URL is required for HTTP/SSE transport"
                )

        server = MCPServers.insert_new_server(
            id=server_id,
            user_id=user.id,
            name=form.name,
            type=form.type,
            form_data=form,
        )

        return server
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/servers/{server_id}", response_model=MCPServerModel)
async def update_server(
    server_id: str,
    form: MCPServerUpdateForm,
    user: Users = Depends(get_current_user)
):
    """Update an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Only owner or admin can update
    if server.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        updated_server = MCPServers.update_server_by_id(server_id, form)
        return updated_server
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/servers/{server_id}")
async def delete_server(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Delete an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Only owner or admin can delete
    if server.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Delete associated resources and tools
        MCPResources.delete_resources_by_server_id(server_id)
        MCPTools.delete_tools_by_server_id(server_id)

        # Delete server
        success = MCPServers.delete_server_by_id(server_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete server")

        return {"success": True, "message": "Server deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/toggle", response_model=MCPServerModel)
async def toggle_server(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Toggle server enabled/disabled status"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Only owner or admin can toggle
    if server.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        updated_server = MCPServers.toggle_server_enabled(server_id)
        return updated_server
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


#####################
# Resources
#####################


@router.get("/servers/{server_id}/resources", response_model=List[dict])
async def list_resources(
    server_id: str,
    refresh: bool = False,
    user: Users = Depends(get_current_user)
):
    """List all resources from an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        # Return cached resources if not refreshing
        if not refresh:
            cached_resources = MCPResources.get_resources_by_server_id(server_id)
            if cached_resources:
                return [
                    {
                        "uri": r.uri,
                        "name": r.name,
                        "description": r.description,
                        "mimeType": r.mime_type,
                    }
                    for r in cached_resources
                ]

        # Connect to server and fetch resources
        client = await get_mcp_client_for_server(server)

        try:
            resources = await client.list_resources()

            # Cache resources
            for resource in resources:
                MCPResources.upsert_resource(
                    server_id=server_id,
                    uri=resource.get("uri"),
                    name=resource.get("name"),
                    description=resource.get("description"),
                    mime_type=resource.get("mimeType"),
                )

            return resources
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")


class ReadResourceRequest(BaseModel):
    uri: str


@router.post("/servers/{server_id}/resources/read")
async def read_resource(
    server_id: str,
    request: ReadResourceRequest,
    user: Users = Depends(get_current_user)
):
    """Read content of a specific resource"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        # Check cache first
        cached_resource = MCPResources.get_resource_by_uri(server_id, request.uri)
        if cached_resource and cached_resource.cached_content:
            # Check if cache is fresh (less than 1 hour old)
            if cached_resource.cached_at and (time.time() - cached_resource.cached_at) < 3600:
                return {
                    "contents": [
                        {
                            "uri": cached_resource.uri,
                            "mimeType": cached_resource.mime_type,
                            "text": cached_resource.cached_content,
                        }
                    ]
                }

        # Fetch from server
        client = await get_mcp_client_for_server(server)

        try:
            result = await client.read_resource(request.uri)

            # Cache the content
            if result and result.get("contents"):
                content_text = result["contents"][0].get("text", "")
                MCPResources.upsert_resource(
                    server_id=server_id,
                    uri=request.uri,
                    content=content_text,
                )

            return result
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(e)}")


#####################
# Tools
#####################


@router.get("/servers/{server_id}/tools", response_model=List[dict])
async def list_tools(
    server_id: str,
    refresh: bool = False,
    user: Users = Depends(get_current_user)
):
    """List all tools from an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        # Return cached tools if not refreshing
        if not refresh:
            cached_tools = MCPTools.get_tools_by_server_id(server_id)
            if cached_tools:
                return [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema,
                    }
                    for t in cached_tools
                ]

        # Connect to server and fetch tools
        client = await get_mcp_client_for_server(server)

        try:
            tools = await client.list_tool_specs()

            # Cache tools
            for tool in tools:
                MCPTools.upsert_tool(
                    server_id=server_id,
                    name=tool.get("name"),
                    description=tool.get("description"),
                    input_schema=tool.get("parameters"),
                )

            return tools
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


class CallToolRequest(BaseModel):
    name: str
    arguments: dict


@router.post("/servers/{server_id}/tools/call")
async def call_tool(
    server_id: str,
    request: CallToolRequest,
    user: Users = Depends(get_current_user)
):
    """Call a tool on an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        client = await get_mcp_client_for_server(server)

        try:
            result = await client.call_tool(request.name, request.arguments)
            return result
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to call tool: {str(e)}")


#####################
# Prompts
#####################


@router.get("/servers/{server_id}/prompts", response_model=List[dict])
async def list_prompts(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """List all prompts from an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        client = await get_mcp_client_for_server(server)

        try:
            prompts = await client.list_prompts()
            return prompts
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")


class GetPromptRequest(BaseModel):
    name: str
    arguments: Optional[dict] = None


@router.post("/servers/{server_id}/prompts/get")
async def get_prompt(
    server_id: str,
    request: GetPromptRequest,
    user: Users = Depends(get_current_user)
):
    """Get a specific prompt from an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    if not server.enabled:
        raise HTTPException(status_code=400, detail="Server is disabled")

    try:
        client = await get_mcp_client_for_server(server)

        try:
            result = await client.get_prompt(request.name, request.arguments)
            return result
        finally:
            await client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")


#####################
# Health & Monitoring
#####################


@router.post("/servers/{server_id}/health")
async def check_server_health(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Check health of an MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if not check_server_access(server, user):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        client = await get_mcp_client_for_server(server)

        try:
            # Try to ping the server
            is_healthy = await client.ping()

            if is_healthy:
                # Get server info
                server_info = await client.get_server_info()

                # Update health status
                MCPServers.update_server_health(
                    server_id,
                    status="healthy",
                    server_info=server_info
                )

                return {
                    "status": "healthy",
                    "server_info": server_info,
                    "timestamp": int(time.time())
                }
            else:
                MCPServers.update_server_health(server_id, status="unhealthy")
                return {
                    "status": "unhealthy",
                    "error": "Server not responding to ping",
                    "timestamp": int(time.time())
                }
        finally:
            await client.disconnect()

    except Exception as e:
        log.exception(e)
        # Update health status to unhealthy
        MCPServers.update_server_health(server_id, status="unhealthy")

        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time())
        }


#####################
# Configuration
#####################


@router.get("/config/generate")
async def generate_config(
    platform: str = "standard",  # standard or windows
    user: Users = Depends(get_current_user)
):
    """Generate MCP configuration file"""
    try:
        # Get all enabled servers for user
        servers = MCPServers.get_servers_by_user_id(user.id, enabled_only=True)

        # Add global servers
        global_servers = MCPServers.get_global_servers(enabled_only=True)
        servers.extend(global_servers)

        # Generate config
        config = {"mcpServers": {}}

        for server in servers:
            if server.type == "stdio":
                config["mcpServers"][server.name] = {
                    "command": server.command,
                    "args": server.args or [],
                    "env": server.env or {},
                    "disabled": False
                }

                # Windows-specific adaptations
                if platform == "windows" and server.command:
                    config["mcpServers"][server.name]["command"] = server.command.replace("/", "\\")

            elif server.type in ["sse", "streamable_http"]:
                config["mcpServers"][server.name] = {
                    "url": server.url,
                    "transport": server.type,
                    "disabled": False
                }

                if server.auth_type == "bearer" and server.auth_config:
                    config["mcpServers"][server.name]["headers"] = {
                        "Authorization": f"Bearer {server.auth_config.get('token', '')}"
                    }

        return config
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/download")
async def download_config(
    platform: str = "standard",
    user: Users = Depends(get_current_user)
):
    """Download MCP configuration as JSON file"""
    try:
        config = await generate_config(platform, user)

        filename = f"mcp_config_{platform}.json"

        return Response(
            content=json.dumps(config, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


#####################
# Admin Functions
#####################


@router.post("/servers/{server_id}/make-global")
async def make_server_global(
    server_id: str,
    user: Users = Depends(get_admin_user)  # Admin only
):
    """Make a server globally accessible (admin only)"""
    server = MCPServers.get_server_by_id(server_id)

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        with get_db() as db:
            server_obj = db.query(MCPServer).filter(MCPServer.id == server_id).first()
            server_obj.is_global = True
            server_obj.updated_at = int(time.time())
            db.commit()
            db.refresh(server_obj)

            return MCPServerModel.model_validate(server_obj)
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# Import get_db if needed for admin functions
from open_webui.internal.db import get_db
from open_webui.models.mcp import MCPServer
