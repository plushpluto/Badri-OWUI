# MCP Configuration Examples

This directory contains example JSON configuration files for importing MCP servers into Open WebUI.

## Import Formats Supported

Open WebUI supports **three different JSON formats** for importing MCP server configurations:

### 1. Standard MCP Config Format (Claude Desktop Compatible)

**File:** `mcp_config_standard.json`

This is the standard format used by Claude Desktop and other MCP clients:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

**Features:**
- ✅ Compatible with Claude Desktop config
- ✅ Can import multiple servers at once
- ✅ Supports stdio servers
- ✅ Environment variables supported

**Use Case:** Import your existing Claude Desktop MCP configuration directly

### 2. Open WebUI Format (Array)

**File:** `mcp_config_openwebui.json`

Open WebUI's native format with full feature support:

```json
[
  {
    "name": "Server Name",
    "description": "Server description",
    "type": "stdio",  // or "sse" or "streamable_http"
    "command": "command",
    "args": ["arg1"],
    "url": "http://...",  // for HTTP/SSE servers
    "env": { "KEY": "value" },
    "auth_type": "bearer",  // for HTTP/SSE servers
    "auth_config": { "token": "..." },
    "is_global": false
  }
]
```

**Features:**
- ✅ Full Open WebUI feature support
- ✅ Supports all transport types (stdio, SSE, HTTP)
- ✅ Authentication configuration
- ✅ Global server settings
- ✅ Import multiple servers at once

**Use Case:** Share configurations between Open WebUI instances

### 3. Single Server Format

**File:** `mcp_single_server.json`

Import a single server configuration:

```json
{
  "name": "Server Name",
  "description": "Description",
  "type": "stdio",
  "command": "command",
  "args": ["arg1"]
}
```

**Features:**
- ✅ Simple and quick
- ✅ Perfect for one-off imports

**Use Case:** Quick single server import

---

## How to Import

### Via Web UI

1. Navigate to **Workspace** → **MCP**
2. Click the **"Import"** button
3. Select your JSON file
4. Servers are automatically created

### What Gets Imported

When you import a configuration:
- ✅ All server names and descriptions
- ✅ Transport configurations (stdio/SSE/HTTP)
- ✅ Commands and arguments
- ✅ Environment variables
- ✅ URLs (for HTTP/SSE servers)
- ✅ Authentication settings
- ❌ Server IDs (new IDs are generated)
- ❌ Health status (checked after import)

---

## Example Servers Included

### `mcp_config_standard.json`

Includes popular MCP servers:
- **filesystem** - Access local files
- **git** - Git repository operations
- **github** - GitHub API integration
- **brave-search** - Web search via Brave
- **postgres** - PostgreSQL database access

### `mcp_config_openwebui.json`

Demonstrates all transport types:
- **Test MCP Server** - Local test server (stdio)
- **GitHub MCP Server** - GitHub integration (stdio)
- **Filesystem MCP Server** - File access (stdio)
- **HTTP MCP Server** - Remote server (HTTP)

### `mcp_single_server.json`

Simple single server example for quick testing.

---

## Customizing Before Import

### Update Paths

Replace placeholder paths with your actual paths:

```json
{
  "command": "python",
  "args": [
    "/path/to/test_mcp_server.py"  // ← Change this!
  ]
}
```

### Update Environment Variables

Add your actual API keys and tokens:

```json
{
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here",  // ← Change this!
    "API_KEY": "your_key_here"  // ← Change this!
  }
}
```

### Set Global Access (Admin Only)

Make servers available to all users:

```json
{
  "is_global": true  // ← Add this for global servers
}
```

---

## Creating Your Own Config

### From Claude Desktop Config

If you have a Claude Desktop config at:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

You can import it directly! Just:
1. Copy the file
2. Click "Import" in Open WebUI
3. Select the file

### From Scratch

Create a JSON file with this structure:

**For stdio servers:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["-m", "my_server"],
      "env": {
        "API_KEY": "xxx"
      }
    }
  }
}
```

**For HTTP servers:**
```json
[
  {
    "name": "My HTTP Server",
    "type": "streamable_http",
    "url": "http://localhost:3000/mcp",
    "auth_type": "bearer",
    "auth_config": {
      "token": "your-token"
    }
  }
]
```

---

## Export Your Configuration

After setting up servers, you can export them:

1. Click **"Export Config"** button
2. Download `mcp_generated_config.json`
3. Use it to:
   - Backup your configuration
   - Share with team members
   - Import on another instance
   - Use with other MCP clients

The exported config is in **Standard MCP format** (Claude Desktop compatible).

---

## Troubleshooting Import

### "Invalid configuration file format"

- Check JSON syntax is valid
- Ensure file has one of the supported formats
- Verify required fields are present (`name`, `type`, etc.)

### Import succeeds but servers show "unhealthy"

- Check command paths are correct
- Verify environment variables are set
- Run health check manually
- Check backend logs for errors

### Some servers fail to import

- Check for duplicate server names
- Verify command executables exist
- Ensure proper permissions for commands
- Review console logs for specific errors

---

## Popular MCP Servers

Here are some popular MCP servers you can add:

### Official Servers (by Anthropic)

```bash
# Filesystem access
npx -y @modelcontextprotocol/server-filesystem /path/to/directory

# GitHub integration
npx -y @modelcontextprotocol/server-github

# Brave Search
npx -y @modelcontextprotocol/server-brave-search

# Google Drive
npx -y @modelcontextprotocol/server-gdrive

# PostgreSQL
npx -y @modelcontextprotocol/server-postgres postgresql://localhost/dbname

# Slack
npx -y @modelcontextprotocol/server-slack

# Puppeteer (web automation)
npx -y @modelcontextprotocol/server-puppeteer
```

### Community Servers

Check the [MCP Servers directory](https://github.com/modelcontextprotocol/servers) for more!

---

## Next Steps

1. **Customize examples** - Update paths and API keys
2. **Import configuration** - Use the Import button
3. **Test servers** - Run health checks
4. **Browse resources** - Explore available resources
5. **Use tools** - Execute MCP tools
6. **Integrate with chat** - Use `@mcp:resource` syntax (coming soon)

---

## Need Help?

- Check `MCP_TESTING_GUIDE.md` for detailed testing instructions
- Review backend logs for import errors
- Verify JSON syntax at https://jsonlint.com
- Ensure MCP servers are installed and accessible

Happy MCP-ing! 🚀
