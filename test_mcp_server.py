#!/usr/bin/env python3
"""
Simple Test MCP Server
This creates a basic MCP server with sample resources and tools for testing.
"""

import asyncio
import json
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    Prompt,
    PromptMessage,
)


# Create MCP server instance
server = Server("test-mcp-server")


@server.list_resources()
async def list_resources():
    """List available resources"""
    return [
        Resource(
            uri="test://greeting",
            name="Greeting Message",
            description="A simple greeting message",
            mimeType="text/plain",
        ),
        Resource(
            uri="test://data",
            name="Sample Data",
            description="Sample JSON data for testing",
            mimeType="application/json",
        ),
        Resource(
            uri="test://timestamp",
            name="Current Timestamp",
            description="Current server timestamp",
            mimeType="text/plain",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str):
    """Read a specific resource"""
    if uri == "test://greeting":
        return TextContent(
            type="text",
            text="Hello from the Test MCP Server! This is a sample resource.",
        )
    elif uri == "test://data":
        data = {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "items": ["item1", "item2", "item3"],
                "count": 3,
            },
        }
        return TextContent(
            type="text",
            text=json.dumps(data, indent=2),
        )
    elif uri == "test://timestamp":
        return TextContent(
            type="text",
            text=f"Current server time: {datetime.now().isoformat()}",
        )
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools():
    """List available tools"""
    return [
        Tool(
            name="echo",
            description="Echo back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo back",
                    }
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number",
                    },
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="get_info",
            description="Get server information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute a tool"""
    if name == "echo":
        message = arguments.get("message", "")
        return [
            TextContent(
                type="text",
                text=f"Echo: {message}",
            )
        ]
    elif name == "add":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return [
            TextContent(
                type="text",
                text=f"Result: {a} + {b} = {result}",
            )
        ]
    elif name == "get_info":
        info = {
            "server_name": "test-mcp-server",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "capabilities": ["resources", "tools", "prompts"],
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(info, indent=2),
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")


@server.list_prompts()
async def list_prompts():
    """List available prompts"""
    return [
        Prompt(
            name="greeting",
            description="Generate a friendly greeting",
            arguments=[
                {
                    "name": "name",
                    "description": "Name to greet",
                    "required": True,
                }
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    """Get a specific prompt"""
    if name == "greeting":
        user_name = arguments.get("name", "User")
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Please greet {user_name} in a friendly and professional manner.",
            ),
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server"""
    print("Starting Test MCP Server...", flush=True)
    print("Server is ready to accept connections via stdio", flush=True)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
