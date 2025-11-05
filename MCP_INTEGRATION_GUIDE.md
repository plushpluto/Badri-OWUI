# Using MCP Servers in Open WebUI

## Understanding the Architecture

### What You Have Now

**MCP Control Panel** (`Workspace → MCP`)
- ✅ Import/Export MCP server configurations
- ✅ Browse resources (files, data, etc.)
- ✅ Execute tools manually
- ✅ Health monitoring
- ❌ NOT connected to chat interface yet

**Settings → Connections** (Model APIs)
- For adding LLM providers (OpenAI, Ollama, etc.)
- Format: `http://api-url/v1/chat/completions`
- **MCP servers don't go here!**

### The Integration Gap

MCP servers are currently **standalone** - you can test them in the MCP workspace, but they're not integrated with the chat interface yet.

---

## 🎯 Three Ways to Use MCP Servers

### Option 1: Manual Testing (Available Now ✅)

**Use the MCP Control Panel to test tools and browse resources manually.**

**Steps:**
1. Go to `Workspace → MCP`
2. Click on a server card
3. Click "🔧 Tools" button
4. Select a tool
5. Fill in parameters
6. Click "Execute"
7. View results

**Use Case:** Testing MCP tools, exploring resources, debugging

---

### Option 2: MCP Tools as Chat Functions (Needs Implementation 🔨)

**Expose MCP tools as Open WebUI functions that AI can call during conversations.**

**How It Would Work:**
```
User: "Search GitHub for issues about authentication"

AI: [Calls MCP github tool]
    Tool: github.search_issues
    Args: { query: "authentication" }

[MCP tool executes]

AI: "I found 15 issues about authentication..."
```

**What's Needed:**
- Create API endpoint: `/api/v1/tools` that lists MCP tools
- Bridge MCP tool calls to function execution
- Register MCP tools dynamically
- Handle tool responses in chat

**Status:** ⚠️ Not implemented yet (this is Phase 4 from the plan)

---

### Option 3: MCP Resources in Chat Context (Needs Implementation 🔨)

**Use @mcp:resource syntax to inject MCP resources into chat context.**

**How It Would Work:**
```
User: "Summarize @mcp:github://issues/123"

[System fetches resource from MCP server]

AI: [Receives issue content in context]
    "This issue is about..."
```

**What's Needed:**
- Chat input parser for `@mcp:resource` syntax
- Autocomplete for MCP resources
- Resource content injection
- Context management

**Status:** ⚠️ Not implemented yet (this is Phase 4 from the plan)

---

## 🚀 Quick Implementation: MCP Tools Bridge

I can implement Option 2 (MCP Tools as Functions) right now. This would:

### What You'll Get:

1. **Automatic Tool Registration**
   - All MCP tools appear in Open WebUI's tool system
   - AI can discover and use them automatically

2. **Seamless Chat Integration**
   - User: "What files are in my desktop?"
   - AI: [Calls filesystem MCP tool]
   - Results appear in chat

3. **Tool Management**
   - Enable/disable MCP tool usage per server
   - Control which tools are available
   - Same permissions as other functions

### Implementation Plan:

**Backend Changes:**
```python
# Add to backend/open_webui/routers/tools.py
@router.get("/")
async def get_tools():
    # Existing tools
    tools = get_existing_tools()

    # Add MCP tools
    mcp_servers = get_enabled_mcp_servers()
    for server in mcp_servers:
        mcp_tools = get_mcp_tools(server)
        tools.extend(convert_to_openwebui_format(mcp_tools))

    return tools

# Add MCP tool execution handler
@router.post("/mcp/{server_id}/{tool_name}/call")
async def call_mcp_tool(server_id, tool_name, args):
    result = await mcp_client.call_tool(server_id, tool_name, args)
    return result
```

**Frontend Changes:**
- Tools automatically appear in function picker
- No UI changes needed!
- Works with existing tool system

### Would You Like Me to Implement This?

If yes, I can create:
1. MCP tool listing endpoint
2. MCP tool execution bridge
3. Tool format conversion
4. Automatic registration system

**ETA:** ~30 minutes

---

## 📝 Current Workaround

Until integration is complete, here's how to use MCP servers:

### For Testing MCP Tools:
1. Go to `Workspace → MCP`
2. Use the Tool Browser
3. Execute tools manually
4. Copy results to chat

### For Using MCP Resources:
1. Go to `Workspace → MCP`
2. Click "📚 Resources" on a server
3. Read resource content
4. Copy/paste into chat context

### For GitHub/API Integrations:
1. Create MCP server in MCP workspace
2. Test tools work correctly
3. Wait for chat integration
4. OR manually call tools and share results

---

## 🎯 What Should We Do Next?

**Quick Win (30 mins):** Implement MCP Tools as Functions
- ✅ Tools work in chat immediately
- ✅ AI can call MCP tools automatically
- ✅ Works with existing Open WebUI architecture

**Future Enhancement:** Resource syntax support
- Implement `@mcp:resource` parsing
- Add autocomplete
- Context injection

---

## 💡 Example: GitHub MCP Server

**Current Way (Manual):**
```
1. Workspace → MCP → GitHub server → Tools
2. Select "search_issues" tool
3. Enter: { "query": "authentication" }
4. Execute
5. Copy result
6. Paste in chat
```

**After Integration (Automatic):**
```
User: "Search GitHub for authentication issues"
AI: [Automatically calls github.search_issues("authentication")]
AI: "I found 15 issues: ..."
```

---

## 🤔 Which Option Do You Want?

**A) Implement MCP Tools Bridge Now** (30 mins)
- Get MCP tools working in chat today
- AI can call tools automatically
- Seamless integration

**B) Manual Testing Only** (Current)
- Use MCP Control Panel to test
- Copy/paste results as needed
- Wait for future integration

**C) Full Integration** (2-3 hours)
- Tools + Resources
- @mcp:resource syntax
- Autocomplete
- Complete Phase 4

---

## 📞 What's Your Use Case?

Help me understand what you want to do:

1. **Just testing MCP servers?**
   → Current MCP Control Panel is perfect

2. **Want AI to use MCP tools in chat?**
   → Let me implement the tools bridge

3. **Need to reference MCP resources in chat?**
   → Need full Phase 4 implementation

4. **Something else?**
   → Tell me what you're trying to achieve!

---

**The short answer to your question:**

There is **no single "MCP server URL"** to add to Settings → Connections because:
- MCP servers are not traditional HTTP APIs
- They use a different protocol (MCP protocol)
- They need a bridge/integration layer to work with chat
- Settings → Connections is only for LLM model providers

**The MCP API endpoints are:**
- Management: `http://localhost:8080/api/v1/mcp/servers`
- Resources: `http://localhost:8080/api/v1/mcp/servers/{id}/resources`
- Tools: `http://localhost:8080/api/v1/mcp/servers/{id}/tools`
- But these aren't meant for direct chat use

Let me know which direction you want to go and I'll implement it! 🚀
