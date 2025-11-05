import json
import logging
import time
from typing import Optional, List
import uuid

from open_webui.internal.db import Base, get_db
from open_webui.env import SRC_LOG_LEVELS

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON, Boolean

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# MCP Server DB Schema
####################


class MCPServer(Base):
    __tablename__ = "mcp_server"

    id = Column(Text, unique=True, primary_key=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text, nullable=True)

    # Server configuration
    type = Column(Text)  # stdio, sse, streamable_http
    command = Column(Text, nullable=True)  # For stdio type
    args = Column(JSON, nullable=True)  # Command arguments
    url = Column(Text, nullable=True)  # For http/sse types
    env = Column(JSON, nullable=True)  # Environment variables

    # Authentication
    auth_type = Column(Text, nullable=True)  # none, bearer, oauth
    auth_config = Column(JSON, nullable=True)  # Auth details

    # Status
    enabled = Column(Boolean, default=True)
    is_global = Column(Boolean, default=False)  # Admin-only global servers
    health_status = Column(Text, nullable=True)  # healthy, unhealthy, unknown
    last_health_check = Column(BigInteger, nullable=True)

    # Metadata
    server_info = Column(JSON, nullable=True)  # Server name, version, capabilities
    meta = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class MCPResource(Base):
    __tablename__ = "mcp_resource"

    id = Column(Text, unique=True, primary_key=True)
    server_id = Column(Text)

    uri = Column(Text)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    mime_type = Column(Text, nullable=True)

    # Caching
    cached_content = Column(Text, nullable=True)
    cached_at = Column(BigInteger, nullable=True)

    created_at = Column(BigInteger)


class MCPTool(Base):
    __tablename__ = "mcp_tool"

    id = Column(Text, unique=True, primary_key=True)
    server_id = Column(Text)

    name = Column(Text)
    description = Column(Text, nullable=True)
    input_schema = Column(JSON, nullable=True)

    created_at = Column(BigInteger)


####################
# Pydantic Models
####################


class MCPServerModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str

    name: str
    description: Optional[str] = None

    type: str  # stdio, sse, streamable_http
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None

    auth_type: Optional[str] = None
    auth_config: Optional[dict] = None

    enabled: bool = True
    is_global: bool = False
    health_status: Optional[str] = None
    last_health_check: Optional[int] = None

    server_info: Optional[dict] = None
    meta: Optional[dict] = None

    created_at: int
    updated_at: int


class MCPResourceModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str

    uri: str
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None

    cached_content: Optional[str] = None
    cached_at: Optional[int] = None

    created_at: int


class MCPToolModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str

    name: str
    description: Optional[str] = None
    input_schema: Optional[dict] = None

    created_at: int


####################
# Forms
####################


class MCPServerForm(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # stdio, sse, streamable_http
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None
    auth_type: Optional[str] = "none"
    auth_config: Optional[dict] = None
    enabled: Optional[bool] = True


class MCPServerUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None
    auth_type: Optional[str] = None
    auth_config: Optional[dict] = None
    enabled: Optional[bool] = None


####################
# Table Classes
####################


class MCPServersTable:
    def insert_new_server(
        self,
        id: str,
        user_id: str,
        name: str,
        type: str,
        form_data: MCPServerForm,
    ) -> Optional[MCPServerModel]:
        with get_db() as db:
            server = MCPServer(
                **{
                    "id": id,
                    "user_id": user_id,
                    "name": name,
                    "description": form_data.description,
                    "type": type,
                    "command": form_data.command,
                    "args": form_data.args,
                    "url": form_data.url,
                    "env": form_data.env,
                    "auth_type": form_data.auth_type,
                    "auth_config": form_data.auth_config,
                    "enabled": form_data.enabled if form_data.enabled is not None else True,
                    "is_global": False,
                    "health_status": "unknown",
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            db.add(server)
            db.commit()
            db.refresh(server)
            return MCPServerModel.model_validate(server)

    def get_server_by_id(self, id: str) -> Optional[MCPServerModel]:
        try:
            with get_db() as db:
                server = db.query(MCPServer).filter(MCPServer.id == id).first()
                return MCPServerModel.model_validate(server) if server else None
        except Exception as e:
            log.exception(e)
            return None

    def get_servers_by_user_id(
        self, user_id: str, enabled_only: bool = False
    ) -> List[MCPServerModel]:
        with get_db() as db:
            query = db.query(MCPServer).filter(MCPServer.user_id == user_id)
            if enabled_only:
                query = query.filter(MCPServer.enabled == True)
            servers = query.all()
            return [MCPServerModel.model_validate(server) for server in servers]

    def get_global_servers(self, enabled_only: bool = False) -> List[MCPServerModel]:
        with get_db() as db:
            query = db.query(MCPServer).filter(MCPServer.is_global == True)
            if enabled_only:
                query = query.filter(MCPServer.enabled == True)
            servers = query.all()
            return [MCPServerModel.model_validate(server) for server in servers]

    def get_all_enabled_servers(self) -> List[MCPServerModel]:
        """Get all enabled servers (global + user-specific)"""
        with get_db() as db:
            servers = db.query(MCPServer).filter(MCPServer.enabled == True).all()
            return [MCPServerModel.model_validate(server) for server in servers]

    def update_server_by_id(
        self, id: str, form_data: MCPServerUpdateForm
    ) -> Optional[MCPServerModel]:
        try:
            with get_db() as db:
                server = db.query(MCPServer).filter(MCPServer.id == id).first()
                if not server:
                    return None

                update_data = form_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(server, key, value)

                server.updated_at = int(time.time())

                db.commit()
                db.refresh(server)
                return MCPServerModel.model_validate(server)
        except Exception as e:
            log.exception(e)
            return None

    def toggle_server_enabled(self, id: str) -> Optional[MCPServerModel]:
        try:
            with get_db() as db:
                server = db.query(MCPServer).filter(MCPServer.id == id).first()
                if not server:
                    return None

                server.enabled = not server.enabled
                server.updated_at = int(time.time())

                db.commit()
                db.refresh(server)
                return MCPServerModel.model_validate(server)
        except Exception as e:
            log.exception(e)
            return None

    def update_server_health(
        self, id: str, status: str, server_info: Optional[dict] = None
    ) -> Optional[MCPServerModel]:
        try:
            with get_db() as db:
                server = db.query(MCPServer).filter(MCPServer.id == id).first()
                if not server:
                    return None

                server.health_status = status
                server.last_health_check = int(time.time())
                if server_info:
                    server.server_info = server_info
                server.updated_at = int(time.time())

                db.commit()
                db.refresh(server)
                return MCPServerModel.model_validate(server)
        except Exception as e:
            log.exception(e)
            return None

    def delete_server_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                server = db.query(MCPServer).filter(MCPServer.id == id).first()
                if not server:
                    return False

                db.delete(server)
                db.commit()
                return True
        except Exception as e:
            log.exception(e)
            return False


class MCPResourcesTable:
    def upsert_resource(
        self,
        server_id: str,
        uri: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Optional[MCPResourceModel]:
        with get_db() as db:
            # Check if resource exists
            resource = (
                db.query(MCPResource)
                .filter(
                    MCPResource.server_id == server_id, MCPResource.uri == uri
                )
                .first()
            )

            if resource:
                # Update existing
                resource.name = name
                resource.description = description
                resource.mime_type = mime_type
                if content:
                    resource.cached_content = content
                    resource.cached_at = int(time.time())
            else:
                # Insert new
                resource = MCPResource(
                    id=str(uuid.uuid4()),
                    server_id=server_id,
                    uri=uri,
                    name=name,
                    description=description,
                    mime_type=mime_type,
                    cached_content=content,
                    cached_at=int(time.time()) if content else None,
                    created_at=int(time.time()),
                )
                db.add(resource)

            db.commit()
            db.refresh(resource)
            return MCPResourceModel.model_validate(resource)

    def get_resources_by_server_id(
        self, server_id: str
    ) -> List[MCPResourceModel]:
        with get_db() as db:
            resources = (
                db.query(MCPResource)
                .filter(MCPResource.server_id == server_id)
                .all()
            )
            return [MCPResourceModel.model_validate(r) for r in resources]

    def get_resource_by_uri(
        self, server_id: str, uri: str
    ) -> Optional[MCPResourceModel]:
        with get_db() as db:
            resource = (
                db.query(MCPResource)
                .filter(
                    MCPResource.server_id == server_id, MCPResource.uri == uri
                )
                .first()
            )
            return MCPResourceModel.model_validate(resource) if resource else None

    def delete_resources_by_server_id(self, server_id: str) -> bool:
        try:
            with get_db() as db:
                db.query(MCPResource).filter(
                    MCPResource.server_id == server_id
                ).delete()
                db.commit()
                return True
        except Exception as e:
            log.exception(e)
            return False


class MCPToolsTable:
    def upsert_tool(
        self,
        server_id: str,
        name: str,
        description: Optional[str] = None,
        input_schema: Optional[dict] = None,
    ) -> Optional[MCPToolModel]:
        with get_db() as db:
            # Check if tool exists
            tool = (
                db.query(MCPTool)
                .filter(MCPTool.server_id == server_id, MCPTool.name == name)
                .first()
            )

            if tool:
                # Update existing
                tool.description = description
                tool.input_schema = input_schema
            else:
                # Insert new
                tool = MCPTool(
                    id=str(uuid.uuid4()),
                    server_id=server_id,
                    name=name,
                    description=description,
                    input_schema=input_schema,
                    created_at=int(time.time()),
                )
                db.add(tool)

            db.commit()
            db.refresh(tool)
            return MCPToolModel.model_validate(tool)

    def get_tools_by_server_id(self, server_id: str) -> List[MCPToolModel]:
        with get_db() as db:
            tools = (
                db.query(MCPTool).filter(MCPTool.server_id == server_id).all()
            )
            return [MCPToolModel.model_validate(t) for t in tools]

    def delete_tools_by_server_id(self, server_id: str) -> bool:
        try:
            with get_db() as db:
                db.query(MCPTool).filter(MCPTool.server_id == server_id).delete()
                db.commit()
                return True
        except Exception as e:
            log.exception(e)
            return False


# Global instances
MCPServers = MCPServersTable()
MCPResources = MCPResourcesTable()
MCPTools = MCPToolsTable()
