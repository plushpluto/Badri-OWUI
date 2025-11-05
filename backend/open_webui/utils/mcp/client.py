import asyncio
import subprocess
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

import logging

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self, server_id: Optional[str] = None):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.server_id = server_id
        self.transport_type: Optional[str] = None

    async def connect_http(self, url: str, headers: Optional[dict] = None):
        """Connect to MCP server via HTTP (streamable_http)"""
        try:
            self.transport_type = "streamable_http"
            self._streams_context = streamablehttp_client(url, headers=headers)

            transport = await self.exit_stack.enter_async_context(self._streams_context)
            read_stream, write_stream, _ = transport

            self._session_context = ClientSession(
                read_stream, write_stream
            )  # pylint: disable=W0201

            self.session = await self.exit_stack.enter_async_context(
                self._session_context
            )

            await self.session.initialize()
            logger.info(f"Connected to MCP server via HTTP: {url}")
        except Exception as e:
            logger.error(f"Failed to connect via HTTP: {e}")
            await self.disconnect()
            raise e

    async def connect_stdio(
        self,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ):
        """Connect to MCP server via stdio"""
        try:
            self.transport_type = "stdio"

            server_params = StdioServerParameters(
                command=command,
                args=args or [],
                env=env or {}
            )

            self._streams_context = stdio_client(server_params)

            transport = await self.exit_stack.enter_async_context(self._streams_context)
            read_stream, write_stream = transport

            self._session_context = ClientSession(read_stream, write_stream)

            self.session = await self.exit_stack.enter_async_context(
                self._session_context
            )

            await self.session.initialize()
            logger.info(f"Connected to MCP server via stdio: {command} {args}")
        except Exception as e:
            logger.error(f"Failed to connect via stdio: {e}")
            await self.disconnect()
            raise e

    async def connect_sse(self, url: str, headers: Optional[dict] = None):
        """Connect to MCP server via SSE (Server-Sent Events)"""
        try:
            self.transport_type = "sse"
            self._streams_context = sse_client(url, headers=headers)

            transport = await self.exit_stack.enter_async_context(self._streams_context)
            read_stream, write_stream = transport

            self._session_context = ClientSession(read_stream, write_stream)

            self.session = await self.exit_stack.enter_async_context(
                self._session_context
            )

            await self.session.initialize()
            logger.info(f"Connected to MCP server via SSE: {url}")
        except Exception as e:
            logger.error(f"Failed to connect via SSE: {e}")
            await self.disconnect()
            raise e

    async def connect(self, url: str, headers: Optional[dict] = None):
        """Legacy method - defaults to HTTP connection"""
        await self.connect_http(url, headers)

    async def list_tool_specs(self) -> Optional[dict]:
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        result = await self.session.list_tools()
        tools = result.tools

        tool_specs = []
        for tool in tools:
            name = tool.name
            description = tool.description

            inputSchema = tool.inputSchema

            # TODO: handle outputSchema if needed
            outputSchema = getattr(tool, "outputSchema", None)

            tool_specs.append(
                {"name": name, "description": description, "parameters": inputSchema}
            )

        return tool_specs

    async def call_tool(
        self, function_name: str, function_args: dict
    ) -> Optional[dict]:
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        result = await self.session.call_tool(function_name, function_args)
        if not result:
            raise Exception("No result returned from MCP tool call.")

        result_dict = result.model_dump(mode="json")
        result_content = result_dict.get("content", {})

        if result.isError:
            raise Exception(result_content)
        else:
            return result_content

    async def list_resources(self, cursor: Optional[str] = None) -> Optional[dict]:
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        result = await self.session.list_resources(cursor=cursor)
        if not result:
            raise Exception("No result returned from MCP list_resources call.")

        result_dict = result.model_dump()
        resources = result_dict.get("resources", [])

        return resources

    async def read_resource(self, uri: str) -> Optional[dict]:
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        result = await self.session.read_resource(uri)
        if not result:
            raise Exception("No result returned from MCP read_resource call.")
        result_dict = result.model_dump()

        return result_dict

    async def list_prompts(self, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available prompts from MCP server"""
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        try:
            result = await self.session.list_prompts(cursor=cursor)
            if not result:
                return []

            result_dict = result.model_dump()
            prompts = result_dict.get("prompts", [])
            return prompts
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []

    async def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific prompt with arguments"""
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        try:
            result = await self.session.get_prompt(name, arguments=arguments or {})
            if not result:
                raise Exception("No result returned from MCP get_prompt call.")

            result_dict = result.model_dump()
            return result_dict
        except Exception as e:
            logger.error(f"Error getting prompt '{name}': {e}")
            raise e

    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information after initialization"""
        if not self.session:
            raise RuntimeError("MCP client is not connected.")

        try:
            # Server info is available after initialize()
            return {
                "server_name": getattr(self.session, "server_name", "Unknown"),
                "server_version": getattr(self.session, "server_version", "Unknown"),
                "protocol_version": getattr(self.session, "protocol_version", "Unknown"),
                "capabilities": getattr(self.session, "capabilities", {}),
            }
        except Exception as e:
            logger.error(f"Error getting server info: {e}")
            return {}

    async def ping(self) -> bool:
        """Check if server is still responsive"""
        if not self.session:
            return False

        try:
            # Try listing resources as a health check
            await self.session.list_resources()
            return True
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    async def disconnect(self):
        """Clean up and close the session"""
        try:
            await self.exit_stack.aclose()
            logger.info(f"Disconnected from MCP server (type: {self.transport_type})")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def __aenter__(self):
        await self.exit_stack.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.exit_stack.__aexit__(exc_type, exc_value, traceback)
        await self.disconnect()
