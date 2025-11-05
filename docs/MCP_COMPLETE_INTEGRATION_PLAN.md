# Open WebUI - Complete MCP Ecosystem Integration Plan

> **Version:** 1.0
> **Date:** 2025-11-05
> **Components:** Core MCP + MCPO Control Panel + MCP Inspector

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Component Overview](#2-component-overview)
- [3. Unified Architecture](#3-unified-architecture)
- [4. Integration Strategy](#4-integration-strategy)
- [5. Implementation Plan](#5-implementation-plan)
- [6. Technical Specifications](#6-technical-specifications)
- [7. UI/UX Design](#7-uiux-design)
- [8. Deployment](#8-deployment)
- [9. Timeline & Resources](#9-timeline--resources)

---

## 1. Executive Summary

This plan integrates **three MCP components** into Open WebUI to create a production-ready, enterprise-grade Model Context Protocol ecosystem:

### Components

1. **Core MCP Integration** - Base MCP client for protocol communication
2. **MCPO Control Panel** - Management interface for MCP orchestrator instances
3. **MCP Inspector** - Official debugging and testing tool

### Combined Benefits

- ✅ **Complete MCP Stack** - Full protocol support from development to production
- ✅ **Visual Management** - GUI for all MCP operations
- ✅ **Developer Tools** - Built-in debugging and testing
- ✅ **Enterprise Ready** - Orchestration, health monitoring, auto-restart
- ✅ **Seamless Integration** - Embedded directly in Open WebUI interface

### Timeline

**Total: 4-5 weeks** (faster than implementing separately)

---

## 2. Component Overview

### 2.1 Core MCP Integration

**Purpose:** Base protocol implementation
**Status:** 30-40% scaffolded (`backend/utils/mcp/client.py`)

**Key Features:**
- MCP client for protocol communication
- Server registry and management
- Resource handling (files, data, prompts)
- Tool/function calling
- Chat integration (`@mcp:resource` syntax)

**Technology:**
- Python (backend)
- TypeScript (frontend)
- HTTP + WebSocket transport

---

### 2.2 MCPO Control Panel

**Repository:** https://github.com/daswer123/mcpo-control-panel
**Purpose:** Web UI + API for managing MCP Orchestrator (mcpo) instances

**Key Features:**
- ✅ **Server Management**: CRUD operations for server definitions
- ✅ **Transport Support**: stdio, SSE, streamable_http types
- ✅ **Configuration Generation**: Auto-generates `mcp_generated_config.json`
- ✅ **Health Monitoring**: Automatic health checks
- ✅ **Auto-Restart**: Restart mcpo on consecutive health check failures
- ✅ **Enable/Disable**: Toggle servers without deletion
- ✅ **Windows Support**: Special configuration for Windows environments

**Technology Stack:**
- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 templates + HTMX
- **Database**: SQLite (SQLModel)
- **Styling**: Materialize CSS
- **API**: RESTful endpoints

**Database Schema:**
```sql
CREATE TABLE server_definition (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- stdio, sse, streamable_http
    command TEXT,
    args TEXT,
    url TEXT,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**API Endpoints:**
```
GET  /api/servers              # List all server definitions
POST /api/servers              # Create new server
GET  /api/servers/{id}         # Get server details
PUT  /api/servers/{id}         # Update server
DELETE /api/servers/{id}       # Delete server
POST /api/servers/{id}/toggle  # Enable/disable server
GET  /api/config/generate      # Generate mcp config
GET  /api/health               # Health check status
POST /api/mcpo/restart         # Restart mcpo instance
```

---

### 2.3 MCP Inspector

**Repository:** https://github.com/modelcontextprotocol/inspector
**Purpose:** Official visual testing and debugging tool for MCP servers

**Key Features:**
- ✅ **Interactive Testing**: Test MCP servers via web UI
- ✅ **Protocol Bridge**: Node.js proxy (MCPP) connects web UI to MCP servers
- ✅ **Transport Support**: stdio, SSE, streamable_http
- ✅ **Configuration Export**: Export configs for Cursor, Claude Code, CLI
- ✅ **Real-time Inspection**: View protocol messages in real-time
- ✅ **Resource Browser**: Explore available resources
- ✅ **Tool Testing**: Test tool/function calls interactively
- ✅ **Prompt Testing**: Test prompt templates
- ✅ **CLI Mode**: Command-line interface for automation

**Technology Stack:**
- **Frontend**: React + TypeScript
- **Backend**: Node.js (MCPP proxy server)
- **Port**: Default 6274
- **Distribution**: npm package (`@modelcontextprotocol/inspector`)

**Components:**
1. **MCPI (MCP Inspector Client)**: React-based web UI
2. **MCPP (MCP Proxy)**: Node.js server acting as protocol bridge

**Usage:**
```bash
# Run via npx (no installation needed)
npx @modelcontextprotocol/inspector node build/index.js

# Or install globally
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```

**Inspector UI Features:**
- Server connection management
- Resource list and details
- Tool/function execution
- Prompt template testing
- Protocol message viewer
- Configuration management
- Export functionality

---

## 3. Unified Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OPEN WEBUI                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Frontend (SvelteKit)                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │ MCP Workspace│  │ MCPO Control │  │ MCP Inspector│        │  │
│  │  │   UI Panel   │  │    Panel     │  │   Embedded   │        │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │  │
│  │  ┌──────────────────────────────────────────────────────────┐ │  │
│  │  │ Chat Interface                                           │ │  │
│  │  │  - @mcp:resource syntax                                  │ │  │
│  │  │  - Resource autocomplete                                 │ │  │
│  │  │  - Tool calling                                          │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Backend (FastAPI)                                           │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │  │
│  │  │ Core MCP Client │  │ MCPO Control API│  │ Inspector    │ │  │
│  │  │  - Resources    │  │  - Server CRUD  │  │   Proxy      │ │  │
│  │  │  - Tools        │  │  - Config Gen   │  │  (Node.js)   │ │  │
│  │  │  - Prompts      │  │  - Health Check │  │              │ │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                    ↓                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  MCP Layer                                                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │ Server      │  │ MCPO        │  │ Health      │          │  │
│  │  │ Registry    │  │ Orchestrator│  │ Monitor     │          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL MCP SERVERS                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Filesystem   │  │ Database     │  │ Git Server   │              │
│  │ MCP Server   │  │ MCP Server   │  │ MCP Server   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Web Search   │  │ Slack API    │  │ Custom Tools │              │
│  │ MCP Server   │  │ MCP Server   │  │ MCP Server   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Interaction Flow

```
User Action Flow:
─────────────────

1. DEVELOPMENT/DEBUGGING:
   User → MCP Inspector (embedded) → Test MCP Server
        → View protocol messages
        → Debug tool calls
        → Export configuration
        ↓
   Configuration → MCPO Control Panel → Save server definition

2. CONFIGURATION/MANAGEMENT:
   User → MCPO Control Panel → Add/Edit MCP Server
        → Enable/Disable servers
        → Generate config
        → Monitor health
        ↓
   Config → MCPO Orchestrator → Manage server lifecycle

3. PRODUCTION USAGE:
   User → Chat Interface → @mcp:file:///README.md
        ↓
   Core MCP Client → MCPO Orchestrator → MCP Server
        ↓
   Resource/Tool Result → Injected into LLM context
        ↓
   Enhanced AI Response → User
```

### 3.3 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Configuration Management                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────┐
    │ MCPO Control Panel                           │
    │ (Server Definitions in SQLite)               │
    └──────────────────────────────────────────────┘
                          ↓
                  Generate Config
                          ↓
    ┌──────────────────────────────────────────────┐
    │ mcp_generated_config.json                    │
    │ {                                            │
    │   "mcpServers": {                            │
    │     "filesystem": {                          │
    │       "command": "node",                     │
    │       "args": ["dist/index.js"],             │
    │       "disabled": false                      │
    │     }                                        │
    │   }                                          │
    │ }                                            │
    └──────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────┐
    │ MCPO Orchestrator                            │
    │ (Manages MCP Server Processes)               │
    └──────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────┐
    │ Running MCP Servers                          │
    │ (stdio/SSE/streamable-http)                  │
    └──────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────┐
    │ Core MCP Client                              │
    │ (Protocol Communication)                     │
    └──────────────────────────────────────────────┘
                          ↓
    ┌──────────────────────────────────────────────┐
    │ Open WebUI Features                          │
    │ (Chat, Functions, Knowledge)                 │
    └──────────────────────────────────────────────┘
```

---

## 4. Integration Strategy

### 4.1 Integration Approach

**Option A: Embedded Integration** (Recommended)
- Integrate MCPO Control Panel and Inspector as **native Open WebUI features**
- Unified authentication and authorization
- Consistent UI/UX with Open WebUI design
- Single deployment

**Option B: Iframe Integration**
- Embed external instances via iframe
- Faster initial implementation
- Less unified experience

**Chosen: Hybrid Approach**
- **MCPO Control Panel**: Rewrite UI in Svelte, use FastAPI backend concepts
- **MCP Inspector**: Embed via iframe initially, native integration later
- **Core MCP**: Native implementation

### 4.2 Why Hybrid?

**MCPO Control Panel - Native:**
- ✅ Simple CRUD operations (easy to replicate)
- ✅ Already uses FastAPI (same as Open WebUI)
- ✅ Better UX when native
- ✅ Unified authentication

**MCP Inspector - Iframe (Phase 1):**
- ✅ Complex React app (preserve upstream updates)
- ✅ Official tool (benefit from community improvements)
- ✅ Faster time to market
- ⚠️ Can migrate to native later if needed

---

## 5. Implementation Plan

### Phase 1: Core MCP Foundation (Week 1)

**Goals:**
- Complete core MCP client
- Database schema for MCP servers
- Basic API endpoints

**Tasks:**

**1.1 Complete MCP Client**
```python
# backend/utils/mcp/client.py - COMPLETE EXISTING

import httpx
import json
from typing import List, Dict, Any, Optional

class MCPClient:
    """Enhanced MCP client with full protocol support"""

    def __init__(
        self,
        server_url: str,
        transport: str = "http",  # http, stdio, sse
        auth_token: Optional[str] = None
    ):
        self.server_url = server_url
        self.transport = transport
        self.auth_token = auth_token

        if transport == "http":
            self.client = httpx.AsyncClient(
                base_url=server_url,
                headers={"Authorization": f"Bearer {auth_token}"} if auth_token else {},
                timeout=30.0
            )

    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection with MCP server"""
        resp = await self.client.post("/initialize", json={
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "Open-WebUI",
                "version": "0.6.34"
            }
        })
        return resp.json()

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        resp = await self.client.post("/resources/list", json={})
        return resp.json().get("resources", [])

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read resource content"""
        resp = await self.client.post("/resources/read", json={"uri": uri})
        return resp.json()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        resp = await self.client.post("/tools/list", json={})
        return resp.json().get("tools", [])

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call MCP tool"""
        resp = await self.client.post("/tools/call", json={
            "name": name,
            "arguments": arguments
        })
        return resp.json()

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        resp = await self.client.post("/prompts/list", json={})
        return resp.json().get("prompts", [])

    async def get_prompt(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get prompt with arguments"""
        resp = await self.client.post("/prompts/get", json={
            "name": name,
            "arguments": arguments or {}
        })
        return resp.json()
```

**1.2 Database Models**
```python
# backend/models/mcp.py - NEW FILE

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON
from open_webui.internal.db import Base

class MCPServer(Base):
    """MCP Server definition (from MCPO Control Panel concept)"""
    __tablename__ = "mcp_server"

    id = Column(String, primary_key=True)
    user_id = Column(String)  # Owner
    name = Column(String, nullable=False)
    description = Column(Text)

    # Server configuration
    type = Column(String, nullable=False)  # stdio, sse, streamable_http
    command = Column(String)  # For stdio type
    args = Column(JSON)  # Command arguments
    url = Column(String)  # For http/sse types
    env = Column(JSON)  # Environment variables

    # Authentication
    auth_type = Column(String)  # none, bearer, oauth
    auth_config = Column(JSON)  # Auth details

    # Status
    enabled = Column(Boolean, default=True)
    is_global = Column(Boolean, default=False)  # Admin-only
    health_status = Column(String)  # healthy, unhealthy, unknown
    last_health_check = Column(Integer)

    # Metadata
    created_at = Column(Integer)
    updated_at = Column(Integer)
    meta = Column(JSON)

class MCPResource(Base):
    """Cached MCP resources for faster lookup"""
    __tablename__ = "mcp_resource"

    id = Column(String, primary_key=True)
    server_id = Column(String)
    uri = Column(String, nullable=False)
    name = Column(String)
    description = Column(Text)
    mime_type = Column(String)
    cached_content = Column(Text)
    cached_at = Column(Integer)
    created_at = Column(Integer)

class MCPTool(Base):
    """Cached MCP tools"""
    __tablename__ = "mcp_tool"

    id = Column(String, primary_key=True)
    server_id = Column(String)
    name = Column(String, nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    created_at = Column(Integer)
```

**1.3 API Router**
```python
# backend/routers/mcp.py - NEW FILE

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from open_webui.utils.auth import get_current_user, get_admin_user
from open_webui.models.users import Users
from open_webui.models.mcp import MCPServer, MCPServers
from open_webui.utils.mcp.client import MCPClient

router = APIRouter(prefix="/mcp", tags=["mcp"])

class MCPServerCreate(BaseModel):
    name: str
    description: str = ""
    type: str  # stdio, sse, streamable_http
    command: Optional[str] = None
    args: Optional[List[str]] = None
    url: Optional[str] = None
    env: Optional[dict] = None
    auth_type: str = "none"
    auth_config: Optional[dict] = None

@router.get("/servers")
async def list_mcp_servers(user: Users = Depends(get_current_user)):
    """List all MCP servers accessible to user"""
    servers = MCPServers.get_servers_by_user_id(user.id)
    if user.role == "admin":
        global_servers = MCPServers.get_global_servers()
        servers.extend(global_servers)
    return servers

@router.post("/servers")
async def create_mcp_server(
    form: MCPServerCreate,
    user: Users = Depends(get_current_user)
):
    """Create new MCP server definition"""
    server = MCPServers.insert_new_server(
        id=str(uuid.uuid4()),
        user_id=user.id,
        **form.dict()
    )
    return server

@router.get("/servers/{server_id}/resources")
async def list_server_resources(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """List resources from MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    # Check access
    if server.user_id != user.id and not server.is_global:
        raise HTTPException(403, "Not authorized")

    # Create MCP client and fetch resources
    client = MCPClient(
        server_url=server.url if server.type != "stdio" else None,
        transport=server.type,
        auth_token=server.auth_config.get("token") if server.auth_config else None
    )

    resources = await client.list_resources()
    return resources

@router.post("/servers/{server_id}/resources/read")
async def read_resource(
    server_id: str,
    uri: str,
    user: Users = Depends(get_current_user)
):
    """Read resource from MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    # Check access
    if server.user_id != user.id and not server.is_global:
        raise HTTPException(403, "Not authorized")

    client = MCPClient(...)
    resource = await client.read_resource(uri)
    return resource

@router.post("/servers/{server_id}/toggle")
async def toggle_server(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Enable/disable MCP server"""
    server = MCPServers.get_server_by_id(server_id)

    # Check ownership
    if server.user_id != user.id:
        raise HTTPException(403, "Not authorized")

    server.enabled = not server.enabled
    MCPServers.update_server(server)

    return {"enabled": server.enabled}
```

### Phase 2: MCPO Control Panel Integration (Week 2)

**Goals:**
- Native UI for server management
- Configuration generation
- Health monitoring

**Tasks:**

**2.1 Backend API (expand on Phase 1)**
```python
# backend/routers/mcp.py - ADD THESE ENDPOINTS

@router.get("/config/generate")
async def generate_mcp_config(user: Users = Depends(get_current_user)):
    """Generate mcp_generated_config.json"""

    # Get all enabled servers for user
    servers = MCPServers.get_enabled_servers_by_user_id(user.id)
    if user.role == "admin":
        global_servers = MCPServers.get_enabled_global_servers()
        servers.extend(global_servers)

    # Generate config format
    config = {"mcpServers": {}}

    for server in servers:
        if server.type == "stdio":
            config["mcpServers"][server.name] = {
                "command": server.command,
                "args": server.args or [],
                "env": server.env or {},
                "disabled": False
            }
        elif server.type in ["sse", "streamable_http"]:
            config["mcpServers"][server.name] = {
                "url": server.url,
                "transport": server.type,
                "disabled": False
            }

    return config

@router.post("/config/download")
async def download_config(
    platform: str = "standard",  # standard or windows
    user: Users = Depends(get_current_user)
):
    """Download mcp_generated_config.json"""

    config = await generate_mcp_config(user)

    # Windows-specific adaptations if needed
    if platform == "windows":
        # Modify paths for Windows
        for server_config in config["mcpServers"].values():
            if "command" in server_config:
                server_config["command"] = server_config["command"].replace("/", "\\")

    return Response(
        content=json.dumps(config, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=mcp_config_{platform}.json"}
    )

@router.post("/health/check")
async def check_server_health(
    server_id: str,
    user: Users = Depends(get_current_user)
):
    """Check health of MCP server"""

    server = MCPServers.get_server_by_id(server_id)

    try:
        client = MCPClient(...)
        await client.initialize()

        # Update health status
        server.health_status = "healthy"
        server.last_health_check = int(time.time())
        MCPServers.update_server(server)

        return {"status": "healthy"}
    except Exception as e:
        server.health_status = "unhealthy"
        server.last_health_check = int(time.time())
        MCPServers.update_server(server)

        return {"status": "unhealthy", "error": str(e)}

@router.post("/health/monitor")
async def start_health_monitoring(
    server_id: str,
    interval: int = 60,  # seconds
    user: Users = Depends(get_admin_user)
):
    """Start continuous health monitoring (admin only)"""

    # Implementation: Background task that checks health periodically
    # and restarts server if unhealthy for N consecutive checks

    # This would use APScheduler or similar
    pass
```

**2.2 Frontend UI**
```svelte
<!-- src/routes/(app)/workspace/mcp/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { user } from '$lib/stores';
  import { toast } from 'svelte-sonner';

  let servers = [];
  let showAddModal = false;
  let newServer = {
    name: '',
    description: '',
    type: 'stdio',
    command: '',
    args: [],
    url: ''
  };

  onMount(async () => {
    await loadServers();
  });

  async function loadServers() {
    const res = await fetch('/api/mcp/servers', {
      headers: { Authorization: `Bearer ${$user.token}` }
    });
    servers = await res.json();
  }

  async function addServer() {
    const res = await fetch('/api/mcp/servers', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${$user.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newServer)
    });

    if (res.ok) {
      toast.success('MCP server added!');
      showAddModal = false;
      await loadServers();
    } else {
      toast.error('Failed to add server');
    }
  }

  async function toggleServer(serverId: string) {
    const res = await fetch(`/api/mcp/servers/${serverId}/toggle`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${$user.token}` }
    });

    if (res.ok) {
      await loadServers();
      toast.success('Server toggled');
    }
  }

  async function checkHealth(serverId: string) {
    toast.info('Checking health...');

    const res = await fetch(`/api/mcp/health/check`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${$user.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ server_id: serverId })
    });

    const result = await res.json();

    if (result.status === 'healthy') {
      toast.success('Server is healthy!');
    } else {
      toast.error(`Server unhealthy: ${result.error}`);
    }

    await loadServers();
  }

  async function downloadConfig(platform = 'standard') {
    const res = await fetch(`/api/mcp/config/download?platform=${platform}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${$user.token}` }
    });

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mcp_config_${platform}.json`;
    a.click();

    toast.success('Config downloaded!');
  }
</script>

<div class="mcp-control-panel p-6">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-2xl font-bold">MCP Control Panel</h1>
    <div class="flex gap-2">
      <button on:click={() => downloadConfig('standard')} class="btn btn-secondary">
        Download Config
      </button>
      <button on:click={() => downloadConfig('windows')} class="btn btn-secondary">
        Download (Windows)
      </button>
      <button on:click={() => showAddModal = true} class="btn btn-primary">
        + Add Server
      </button>
    </div>
  </div>

  <!-- Servers Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each servers as server}
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="card-title">{server.name}</h2>
              <p class="text-sm text-gray-600">{server.description}</p>
            </div>
            <div class="badge badge-{server.enabled ? 'success' : 'error'}">
              {server.enabled ? 'Enabled' : 'Disabled'}
            </div>
          </div>

          <div class="divider"></div>

          <div class="space-y-2 text-sm">
            <div><strong>Type:</strong> {server.type}</div>
            {#if server.type === 'stdio'}
              <div><strong>Command:</strong> {server.command}</div>
            {:else}
              <div><strong>URL:</strong> {server.url}</div>
            {/if}
            <div>
              <strong>Health:</strong>
              <span class="badge badge-{server.health_status === 'healthy' ? 'success' : 'warning'}">
                {server.health_status || 'unknown'}
              </span>
            </div>
          </div>

          <div class="card-actions justify-end mt-4">
            <button on:click={() => checkHealth(server.id)} class="btn btn-sm btn-ghost">
              🏥 Check Health
            </button>
            <button on:click={() => toggleServer(server.id)} class="btn btn-sm btn-primary">
              {server.enabled ? 'Disable' : 'Enable'}
            </button>
          </div>
        </div>
      </div>
    {/each}
  </div>

  <!-- Add Server Modal -->
  {#if showAddModal}
    <div class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">Add MCP Server</h3>

        <div class="form-control">
          <label class="label">Server Name</label>
          <input bind:value={newServer.name} class="input input-bordered" />
        </div>

        <div class="form-control">
          <label class="label">Description</label>
          <textarea bind:value={newServer.description} class="textarea textarea-bordered"></textarea>
        </div>

        <div class="form-control">
          <label class="label">Transport Type</label>
          <select bind:value={newServer.type} class="select select-bordered">
            <option value="stdio">stdio (Local process)</option>
            <option value="sse">SSE (Server-Sent Events)</option>
            <option value="streamable_http">Streamable HTTP</option>
          </select>
        </div>

        {#if newServer.type === 'stdio'}
          <div class="form-control">
            <label class="label">Command</label>
            <input bind:value={newServer.command} class="input input-bordered" placeholder="node" />
          </div>

          <div class="form-control">
            <label class="label">Arguments (comma-separated)</label>
            <input
              value={newServer.args.join(', ')}
              on:input={e => newServer.args = e.target.value.split(',').map(s => s.trim())}
              class="input input-bordered"
              placeholder="dist/index.js"
            />
          </div>
        {:else}
          <div class="form-control">
            <label class="label">Server URL</label>
            <input bind:value={newServer.url} class="input input-bordered" placeholder="http://localhost:3000" />
          </div>
        {/if}

        <div class="modal-action">
          <button on:click={() => showAddModal = false} class="btn">Cancel</button>
          <button on:click={addServer} class="btn btn-primary">Add Server</button>
        </div>
      </div>
    </div>
  {/if}
</div>
```

### Phase 3: MCP Inspector Integration (Week 3)

**Goals:**
- Embed MCP Inspector for testing/debugging
- Provide seamless access from MCP workspace

**Tasks:**

**3.1 Inspector Proxy**
```python
# backend/utils/mcp/inspector.py - NEW FILE

import subprocess
import asyncio
from typing import Optional

class MCPInspectorManager:
    """Manage MCP Inspector instance"""

    def __init__(self, port: int = 6274):
        self.port = port
        self.process: Optional[subprocess.Popen] = None

    def start(self):
        """Start MCP Inspector"""
        if self.process:
            return  # Already running

        # Start inspector via npx
        self.process = subprocess.Popen(
            ['npx', '@modelcontextprotocol/inspector', 'node', 'build/index.js'],
            env={'PORT': str(self.port)}
        )

    def stop(self):
        """Stop MCP Inspector"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def is_running(self) -> bool:
        """Check if inspector is running"""
        return self.process is not None and self.process.poll() is None

# Global instance
inspector_manager = MCPInspectorManager()
```

**3.2 API Endpoints**
```python
# backend/routers/mcp.py - ADD

from open_webui.utils.mcp.inspector import inspector_manager

@router.post("/inspector/start")
async def start_inspector(user: Users = Depends(get_current_user)):
    """Start MCP Inspector"""
    inspector_manager.start()
    return {"status": "started", "url": f"http://localhost:{inspector_manager.port}"}

@router.post("/inspector/stop")
async def stop_inspector(user: Users = Depends(get_admin_user)):
    """Stop MCP Inspector (admin only)"""
    inspector_manager.stop()
    return {"status": "stopped"}

@router.get("/inspector/status")
async def inspector_status(user: Users = Depends(get_current_user)):
    """Check inspector status"""
    return {
        "running": inspector_manager.is_running(),
        "url": f"http://localhost:{inspector_manager.port}" if inspector_manager.is_running() else None
    }
```

**3.3 Frontend Integration**
```svelte
<!-- src/routes/(app)/workspace/mcp/inspector/+page.svelte -->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { user } from '$lib/stores';

  let inspectorRunning = false;
  let inspectorUrl = '';

  onMount(async () => {
    await checkInspectorStatus();
  });

  async function checkInspectorStatus() {
    const res = await fetch('/api/mcp/inspector/status', {
      headers: { Authorization: `Bearer ${$user.token}` }
    });
    const data = await res.json();
    inspectorRunning = data.running;
    inspectorUrl = data.url;
  }

  async function startInspector() {
    const res = await fetch('/api/mcp/inspector/start', {
      method: 'POST',
      headers: { Authorization: `Bearer ${$user.token}` }
    });
    const data = await res.json();
    inspectorUrl = data.url;
    inspectorRunning = true;
  }
</script>

<div class="mcp-inspector-page p-6">
  <div class="flex justify-between items-center mb-4">
    <h1 class="text-2xl font-bold">MCP Inspector</h1>
    {#if !inspectorRunning}
      <button on:click={startInspector} class="btn btn-primary">
        Start Inspector
      </button>
    {/if}
  </div>

  {#if inspectorRunning}
    <div class="inspector-container">
      <iframe
        src={inspectorUrl}
        title="MCP Inspector"
        class="w-full h-[calc(100vh-12rem)] border rounded"
      />
    </div>
  {:else}
    <div class="text-center py-12">
      <p class="text-gray-600 mb-4">MCP Inspector is not running</p>
      <button on:click={startInspector} class="btn btn-primary">
        Launch Inspector
      </button>
    </div>
  {/if}
</div>
```

### Phase 4: Chat Integration (Week 4)

**Goals:**
- `@mcp:resource` syntax
- Autocomplete for MCP resources
- Seamless context injection

**Tasks:**

**4.1 Chat Parser**
```typescript
// src/lib/utils/mcp.ts - NEW FILE

export function parseMCPReferences(message: string): MCPReference[] {
  const regex = /@mcp:([a-zA-Z0-9_-]+):(.+?)(?:\s|$)/g;
  const references: MCPReference[] = [];

  let match;
  while ((match = regex.exec(message)) !== null) {
    references.push({
      serverId: match[1],
      resourceUri: match[2],
      fullMatch: match[0]
    });
  }

  return references;
}

export async function resolveMCPReferences(
  message: string,
  token: string
): Promise<string> {
  const references = parseMCPReferences(message);
  let enhancedMessage = message;

  for (const ref of references) {
    // Fetch resource content
    const res = await fetch(`/api/mcp/servers/${ref.serverId}/resources/read`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ uri: ref.resourceUri })
    });

    const resource = await res.json();

    // Replace reference with content
    const contextBlock = `\n\n[MCP Resource: ${ref.resourceUri}]\n${resource.content}\n[End MCP Resource]\n\n`;
    enhancedMessage = enhancedMessage.replace(ref.fullMatch, contextBlock);
  }

  return enhancedMessage;
}
```

**4.2 Chat Input Component**
```svelte
<!-- Update src/lib/components/chat/MessageInput.svelte -->

<script lang="ts">
  import { parseMCPReferences, resolveMCPReferences } from '$lib/utils/mcp';

  let message = '';
  let showMCPAutocomplete = false;
  let mcpServers = [];
  let mcpResources = [];

  async function handleInput(e) {
    message = e.target.value;

    // Check for @mcp: trigger
    const cursorPos = e.target.selectionStart;
    const textBeforeCursor = message.substring(0, cursorPos);

    if (textBeforeCursor.endsWith('@mcp:')) {
      // Show MCP server autocomplete
      await loadMCPServers();
      showMCPAutocomplete = true;
    } else if (textBeforeCursor.match(/@mcp:([a-zA-Z0-9_-]+):$/)) {
      // Show resource autocomplete for selected server
      const match = textBeforeCursor.match(/@mcp:([a-zA-Z0-9_-]+):$/);
      await loadMCPResources(match[1]);
      showMCPAutocomplete = true;
    } else {
      showMCPAutocomplete = false;
    }
  }

  async function sendMessage() {
    // Resolve MCP references before sending
    const enhancedMessage = await resolveMCPReferences(message, $user.token);

    // Send enhanced message to LLM
    await sendToLLM(enhancedMessage);
  }
</script>

<div class="message-input-container">
  <textarea
    bind:value={message}
    on:input={handleInput}
    placeholder="Type a message... Use @mcp:server:resource to reference MCP resources"
  />

  {#if showMCPAutocomplete}
    <div class="autocomplete-dropdown">
      <!-- MCP autocomplete UI -->
    </div>
  {/if}

  <button on:click={sendMessage}>Send</button>
</div>
```

### Phase 5: Polish & Testing (Week 5)

**Goals:**
- End-to-end testing
- Documentation
- Performance optimization

**Tasks:**
- Write unit tests for MCP client
- Write integration tests for all APIs
- E2E tests for chat integration
- Performance optimization
- User documentation
- Video tutorials

---

## 6. Technical Specifications

### 6.1 API Specifications

**MCP Protocol Version:** `2025-06-18`

**Transport Support:**
- ✅ HTTP (JSON-RPC over HTTP)
- ✅ SSE (Server-Sent Events)
- ✅ stdio (Standard input/output)

**Core Capabilities:**
- Resources (read, list)
- Tools (call, list)
- Prompts (get, list)
- Sampling (optional)
- Roots (optional, listChanged)

### 6.2 Database Schema

```sql
-- MCP Servers
CREATE TABLE mcp_server (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,  -- stdio, sse, streamable_http
    command TEXT,
    args TEXT,  -- JSON array
    url TEXT,
    env TEXT,  -- JSON object
    auth_type TEXT,
    auth_config TEXT,  -- JSON object
    enabled BOOLEAN DEFAULT 1,
    is_global BOOLEAN DEFAULT 0,
    health_status TEXT,
    last_health_check INTEGER,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    meta TEXT,  -- JSON
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- MCP Resources (Cache)
CREATE TABLE mcp_resource (
    id TEXT PRIMARY KEY,
    server_id TEXT NOT NULL,
    uri TEXT NOT NULL,
    name TEXT,
    description TEXT,
    mime_type TEXT,
    cached_content TEXT,
    cached_at INTEGER,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (server_id) REFERENCES mcp_server(id)
);

-- MCP Tools (Cache)
CREATE TABLE mcp_tool (
    id TEXT PRIMARY KEY,
    server_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    input_schema TEXT,  -- JSON
    created_at INTEGER NOT NULL,
    FOREIGN KEY (server_id) REFERENCES mcp_server(id)
);

-- Indexes
CREATE INDEX idx_mcp_server_user_id ON mcp_server(user_id);
CREATE INDEX idx_mcp_server_enabled ON mcp_server(enabled);
CREATE INDEX idx_mcp_resource_server_id ON mcp_resource(server_id);
CREATE INDEX idx_mcp_tool_server_id ON mcp_tool(server_id);
```

### 6.3 Configuration Format

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "HOME": "/home/user"
      },
      "disabled": false
    },
    "database": {
      "url": "http://localhost:3100",
      "transport": "sse",
      "disabled": false
    }
  }
}
```

---

## 7. UI/UX Design

### 7.1 Navigation Structure

```
Open WebUI
├── Chat (existing)
├── Workspace
│   ├── Models (existing)
│   ├── Prompts (existing)
│   ├── Functions (existing)
│   ├── Knowledge (existing)
│   └── MCP (NEW)
│       ├── Servers (MCPO Control Panel UI)
│       │   ├── List servers
│       │   ├── Add/Edit server
│       │   ├── Enable/Disable
│       │   ├── Health checks
│       │   └── Generate config
│       ├── Resources (Browse MCP resources)
│       ├── Tools (Browse MCP tools)
│       └── Inspector (Embedded MCP Inspector)
└── Admin (existing)
```

### 7.2 Key UI Components

**1. MCP Server Card**
```
┌────────────────────────────────────────┐
│ Filesystem Server          [Enabled ✓] │
├────────────────────────────────────────┤
│ Type: stdio                            │
│ Command: node dist/index.js            │
│ Health: ● Healthy                      │
│ Last Check: 2 minutes ago              │
├────────────────────────────────────────┤
│ [Check Health] [Edit] [Disable]       │
└────────────────────────────────────────┘
```

**2. Resource Browser**
```
┌────────────────────────────────────────┐
│ MCP Resources                   [🔍]   │
├────────────────────────────────────────┤
│ Server: Filesystem ▼                   │
├────────────────────────────────────────┤
│ 📄 file:///README.md                   │
│ 📄 file:///package.json                │
│ 📁 file:///src/                        │
│   📄 file:///src/index.ts              │
│   📄 file:///src/utils.ts              │
├────────────────────────────────────────┤
│ [Use in Chat] [Preview]                │
└────────────────────────────────────────┘
```

**3. Chat Input with MCP Autocomplete**
```
┌────────────────────────────────────────┐
│ @mcp:filesystem:█                      │
│ ┌──────────────────────────────┐      │
│ │ 📄 file:///README.md         │      │
│ │ 📄 file:///package.json      │      │
│ │ 📁 file:///src/              │      │
│ └──────────────────────────────┘      │
└────────────────────────────────────────┘
```

---

## 8. Deployment

### 8.1 Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      # MCP Configuration
      - MCP_ENABLED=true
      - MCP_INSPECTOR_ENABLED=true
      - MCP_INSPECTOR_PORT=6274
      - MCPO_ENABLED=true

      # Database
      - DATABASE_URL=postgresql://user:pass@postgres:5432/openwebui

      # Other configs...
    volumes:
      - open-webui-data:/app/backend/data
      - mcp-config:/app/mcp_config
    depends_on:
      - postgres
      - mcpo-orchestrator

  mcpo-orchestrator:
    image: daswer123/mcpo:latest
    ports:
      - "3100:3100"
    volumes:
      - mcp-config:/config
      - mcp-servers:/servers
    environment:
      - CONFIG_PATH=/config/mcp_generated_config.json

  mcp-inspector:
    image: modelcontextprotocol/inspector:latest
    ports:
      - "6274:6274"
    environment:
      - PORT=6274

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=openwebui
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  open-webui-data:
  mcp-config:
  mcp-servers:
  postgres-data:
```

### 8.2 Environment Variables

```bash
# .env

# MCP Core
MCP_ENABLED=true
MCP_AUTO_DISCOVER=true  # Auto-discover MCP servers

# MCPO Control Panel
MCPO_ENABLED=true
MCPO_URL=http://localhost:3100
MCPO_AUTO_RESTART=true
MCPO_HEALTH_CHECK_INTERVAL=60  # seconds

# MCP Inspector
MCP_INSPECTOR_ENABLED=true
MCP_INSPECTOR_PORT=6274
MCP_INSPECTOR_AUTO_START=false  # Start on demand

# MCP Servers (example)
MCP_SERVER_FILESYSTEM_ENABLED=true
MCP_SERVER_FILESYSTEM_COMMAND=node
MCP_SERVER_FILESYSTEM_ARGS=dist/index.js

MCP_SERVER_DATABASE_ENABLED=true
MCP_SERVER_DATABASE_URL=http://localhost:3200
```

---

## 9. Timeline & Resources

### 9.1 Development Timeline

**Total: 4-5 weeks**

| Week | Phase | Deliverables | Effort |
|------|-------|--------------|--------|
| 1 | Core MCP Foundation | MCP client, DB models, basic API | 40 hrs |
| 2 | MCPO Control Panel | Server management UI, config generation, health monitoring | 35 hrs |
| 3 | MCP Inspector | Iframe integration, proxy management | 30 hrs |
| 4 | Chat Integration | @mcp: syntax, autocomplete, context injection | 35 hrs |
| 5 | Polish & Testing | Tests, docs, optimization | 30 hrs |
| **Total** | | **Complete MCP Ecosystem** | **170 hrs** |

### 9.2 Team Requirements

**Minimum Team:**
- 1 Full-Stack Developer (Python + TypeScript)
- 1 Part-time QA Engineer (testing phase)

**Ideal Team:**
- 1 Backend Developer (Python/FastAPI)
- 1 Frontend Developer (Svelte/TypeScript)
- 1 QA Engineer (part-time)

### 9.3 Dependencies

**External:**
- MCPO Control Panel (https://github.com/daswer123/mcpo-control-panel) - inspiration/reference
- MCP Inspector (https://github.com/modelcontextprotocol/inspector) - embed as-is
- MCP Protocol Spec (https://modelcontextprotocol.io/specification/2025-06-18)

**Internal:**
- Open WebUI v0.6.34+
- FastAPI backend
- SvelteKit frontend
- SQLite/PostgreSQL database

### 9.4 Success Metrics

**Technical:**
- ✅ All MCP protocol operations supported
- ✅ <100ms latency for resource reads (cached)
- ✅ 99.9% uptime for MCP servers
- ✅ Health monitoring with auto-restart

**User Experience:**
- ✅ Intuitive server management UI
- ✅ Seamless chat integration
- ✅ Helpful autocomplete
- ✅ Clear error messages

**Adoption:**
- ✅ 50% of users add at least 1 MCP server
- ✅ 25% of chats use @mcp: references
- ✅ Positive user feedback (>4.5/5)

---

## 10. Benefits Summary

### 10.1 For Users

✅ **Access to MCP Ecosystem** - 100+ community MCP servers
✅ **Unified Interface** - Manage everything in Open WebUI
✅ **Enhanced AI Responses** - Real-time context from any source
✅ **Easy Debugging** - Built-in inspector tool
✅ **Enterprise Ready** - Health monitoring, auto-restart

### 10.2 For Developers

✅ **Standard Protocol** - Industry-standard MCP
✅ **Easy Integration** - Well-documented APIs
✅ **Debugging Tools** - Official inspector included
✅ **Extensible** - Add custom MCP servers easily
✅ **Future-Proof** - Adopted by OpenAI, Anthropic, Google

### 10.3 For Admins

✅ **Centralized Management** - Single control panel
✅ **Health Monitoring** - Proactive issue detection
✅ **Configuration Export** - Easy backup/migration
✅ **Access Control** - User/group permissions
✅ **Audit Logging** - Track all MCP operations

---

## Next Steps

**Immediate Actions:**

1. ✅ Review this integration plan
2. ✅ Approve architecture and approach
3. ✅ Set up development environment
4. ✅ Begin Phase 1 implementation

**Want me to start implementing?**

I can begin with **Phase 1: Core MCP Foundation** right now, which includes:
- Completing the MCP client
- Adding database models
- Creating initial API endpoints

**Shall I proceed?** 🚀

---

**Document Version:** 1.0
**Created:** 2025-11-05
**Author:** Claude (Open WebUI Integration Specialist)
**Status:** Ready for Implementation
