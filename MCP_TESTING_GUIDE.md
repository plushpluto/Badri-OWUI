# 🧪 MCP Integration Testing Guide

Complete guide to test the Model Context Protocol (MCP) integration in Open WebUI.

## Prerequisites

### 1. Fix File Watcher Limits (If Not Already Done)

```bash
# Increase system file watcher limits
sudo sysctl fs.inotify.max_user_watches=524288
sudo sysctl fs.inotify.max_user_instances=512
sudo sysctl -p

# Verify the changes
cat /proc/sys/fs/inotify/max_user_watches  # Should show 524288
```

### 2. Install MCP Python Package (For Test Server)

```bash
# Install the official MCP Python SDK
pip install mcp
```

---

## Part 1: Start Servers

### Step 1: Start Backend Server

```bash
cd backend

# Option A: Using the built-in command
python -m open_webui serve

# Option B: Using uvicorn directly
uvicorn open_webui.main:app --reload --host 0.0.0.0 --port 8080
```

**✅ Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade a5c220713937 -> mcp_001_initial, Add MCP (Model Context Protocol) tables
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**🔍 Verify Migration Ran:**
The key line is:
```
Running upgrade a5c220713937 -> mcp_001_initial, Add MCP (Model Context Protocol) tables
```

### Step 2: Start Frontend Server

```bash
# In project root directory
npm run dev
```

**✅ Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

---

## Part 2: Access MCP Control Panel

### Step 1: Open Browser

Navigate to: `http://localhost:5173` (or your frontend URL)

### Step 2: Login

Use your Open WebUI credentials to login.

### Step 3: Navigate to MCP Workspace

Click: **Workspace** → **MCP** tab

**✅ Expected View:**
- Page title: "MCP Servers"
- Empty state message: "No MCP servers configured"
- Button: "Create Your First Server"
- Button: "Export Config"
- Button: "New Server" (+)

---

## Part 3: Create Test MCP Server

### Step 1: Start Test MCP Server

In a new terminal:

```bash
cd /path/to/Badri-OWUI

# Make the test server executable
chmod +x test_mcp_server.py

# Verify MCP is installed
python -c "import mcp; print('MCP installed successfully')"

# The test server will be started by Open WebUI when you create it
```

### Step 2: Create Server via UI

1. Click **"New Server"** button
2. Fill in the form:

**Server Details:**
- **Name:** `Test MCP Server`
- **Description:** `Local test server for MCP testing`
- **Transport Type:** `Stdio (Local Process)`

**Stdio Configuration:**
- **Command:** `python` (or `python3`)
- **Arguments:** (one per line)
  ```
  /home/rangarb/badri/Badri-OWUI/test_mcp_server.py
  ```
  *(Replace with your actual path - use `pwd` to get it)*

**Environment Variables:** (leave empty for this test)

**Access:**
- ☐ Make this server available to all users (global)

3. Click **"Create"**

**✅ Expected Result:**
- Success toast: "MCP server created successfully"
- Server card appears in the list
- Health status: Initially "unknown" (gray dot)

---

## Part 4: Test Server Features

### Test 1: Health Check

1. Click the **"🩺 Health Check"** button on your server card
2. Wait for the check to complete (~2 seconds)

**✅ Expected Result:**
- Success toast: "Server is healthy"
- Health status changes to "healthy" (green dot)
- Server info appears below the card:
  - Server Name: `test-mcp-server`
  - Version: `1.0.0`
  - Protocol: `2024-11-05` (or similar)

### Test 2: Browse Resources

1. Click the **"📚 Resources"** button
2. A modal opens with two panels

**✅ Expected Result - Left Panel (Resource List):**
- "Greeting Message" - A simple greeting message
- "Sample Data" - Sample JSON data for testing
- "Current Timestamp" - Current server timestamp

**✅ Test Resource Reading:**
1. Click on **"Greeting Message"**
2. Right panel shows:
   ```
   Hello from the Test MCP Server! This is a sample resource.
   ```

3. Click on **"Sample Data"**
4. Right panel shows formatted JSON:
   ```json
   {
     "status": "active",
     "timestamp": "2025-11-05T...",
     "data": {
       "items": ["item1", "item2", "item3"],
       "count": 3
     }
   }
   ```

5. Click **"Refresh"** button - resources update
6. Close modal with ✕ button

### Test 3: Browse and Execute Tools

1. Click the **"🔧 Tools"** button
2. A modal opens with two panels

**✅ Expected Result - Left Panel (Tool List):**
- `echo` - Echo back the input message
- `add` - Add two numbers together
- `get_info` - Get server information

**✅ Test Tool Execution:**

#### Test 3a: Echo Tool
1. Click **"echo"** in the tool list
2. Right panel shows:
   - Parameter: `message` (text field)
3. Enter: `Hello MCP!`
4. Click **"▶️ Execute Tool"**
5. Result appears:
   ```
   Echo: Hello MCP!
   ```

#### Test 3b: Add Tool
1. Click **"add"** in the tool list
2. Right panel shows:
   - Parameter: `a` (number field)
   - Parameter: `b` (number field)
3. Enter: `a = 10`, `b = 25`
4. Click **"▶️ Execute Tool"**
5. Result appears:
   ```
   Result: 10 + 25 = 35
   ```

#### Test 3c: Get Info Tool
1. Click **"get_info"** in the tool list
2. Shows: "No parameters required"
3. Click **"▶️ Execute Tool"**
4. Result appears with JSON:
   ```json
   {
     "server_name": "test-mcp-server",
     "version": "1.0.0",
     "timestamp": "...",
     "capabilities": ["resources", "tools", "prompts"]
   }
   ```

### Test 4: Server Management

#### Test 4a: Disable Server
1. Hover over the server card
2. Click the **⋯** (three dots) menu button
3. Click **"Disable"**
4. Success toast: "MCP server disabled"
5. Badge appears: "Disabled"

#### Test 4b: Enable Server
1. Click **⋯** menu again
2. Click **"Enable"**
3. Success toast: "MCP server enabled"
4. "Disabled" badge disappears

#### Test 4c: Edit Server
1. Click **⋯** menu
2. Click **"Edit"**
3. Modal opens with pre-filled form
4. Change description to: `Updated test server`
5. Click **"Save"**
6. Success toast: "MCP server updated successfully"
7. Description updates on the card

### Test 5: Config Export

1. Click **"Export Config"** button (top right)
2. File downloads: `mcp_generated_config.json`
3. Open the file

**✅ Expected Content:**
```json
{
  "mcpServers": {
    "test-mcp-server": {
      "command": "python",
      "args": [
        "/home/rangarb/badri/Badri-OWUI/test_mcp_server.py"
      ]
    }
  }
}
```

### Test 6: Search and Filter

1. In the search box, type: `test`
2. Server card remains visible
3. Type: `xyz`
4. Message: "No MCP servers found matching your search"
5. Clear search (✕ button)
6. Server card reappears

---

## Part 5: Test Advanced Features (Optional)

### Test HTTP/SSE Server (If Available)

If you have an MCP server running on HTTP:

1. Click **"New Server"**
2. Select **"HTTP (Streamable HTTP)"**
3. Enter URL: `http://localhost:3000/mcp`
4. Create and test similarly

### Test Global Access (Admin Only)

If you're logged in as admin:

1. Edit server
2. Check **"Make this server available to all users (global)"**
3. Save
4. Badge appears: "Global"
5. Log in as different user
6. Navigate to MCP workspace
7. Global server is visible to other users

---

## Part 6: Test Error Handling

### Test 6a: Invalid Server

1. Create new server with invalid command: `invalid_command`
2. Try health check
3. Error toast: "Health check failed"
4. Status shows "unhealthy" (red dot)

### Test 6b: Delete Server

1. Click **⋯** menu on test server
2. Click **"Delete"** (red option at bottom)
3. Confirmation dialog appears
4. Click **"Confirm"**
5. Success toast: "MCP server deleted successfully"
6. Server card disappears

---

## 🎯 Testing Checklist

Use this checklist to track your testing:

### Backend
- [ ] Backend starts without errors
- [ ] Migration runs successfully (check logs)
- [ ] MCP tables created (mcp_server, mcp_resource, mcp_tool)
- [ ] API endpoints accessible at `/api/v1/mcp/*`

### Frontend Navigation
- [ ] MCP tab visible in Workspace menu
- [ ] MCP page loads at `/workspace/mcp`
- [ ] Empty state displays correctly
- [ ] "New Server" button works

### Server Management
- [ ] Create stdio server successfully
- [ ] Server card displays with correct info
- [ ] Health check works and updates status
- [ ] Enable/disable toggle works
- [ ] Edit server updates information
- [ ] Delete server removes from list
- [ ] Search/filter functionality works

### Resource Browser
- [ ] Resources list loads
- [ ] Can select and view resource content
- [ ] Refresh button updates list
- [ ] Modal opens and closes properly
- [ ] Search within resources works

### Tool Browser
- [ ] Tools list loads
- [ ] Tool details display correctly
- [ ] Parameter forms generate dynamically
- [ ] Can execute tools with parameters
- [ ] Results display properly
- [ ] Different parameter types work (string, number, boolean)

### Config Export
- [ ] Config file downloads
- [ ] JSON format is correct
- [ ] Contains all enabled servers

### UI/UX
- [ ] Dark mode support works
- [ ] Responsive layout (test mobile view)
- [ ] Loading spinners appear during operations
- [ ] Toast notifications display for all actions
- [ ] Icons and badges display correctly

---

## 🐛 Troubleshooting

### Issue: Migration Not Running

**Check:**
```bash
cd backend
python -c "from open_webui.models.mcp import MCPServers; print('MCP models loaded')"
```

**Fix:**
```bash
# Manually run migration
cd backend
alembic upgrade head
```

### Issue: Test Server Won't Start

**Check MCP Installation:**
```bash
pip install mcp
python -c "import mcp; print(mcp.__version__)"
```

**Check Test Server:**
```bash
python test_mcp_server.py
# Should print: "Starting Test MCP Server..."
# Press Ctrl+C to stop
```

### Issue: Resources/Tools Not Loading

**Check Console Logs:**
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed API calls

**Check Backend Logs:**
- Look for errors in backend terminal
- Check for MCP client connection errors

### Issue: "No such table: mcp_server"

**Solution:**
```bash
# Backend wasn't properly migrated
cd backend
python -c "from open_webui.config import run_migrations; run_migrations()"
```

---

## 📊 Expected Performance

- **Server Creation:** < 2 seconds
- **Health Check:** 1-3 seconds
- **Resource List:** < 1 second
- **Resource Read:** < 1 second
- **Tool Execution:** 1-2 seconds
- **Config Export:** Instant

---

## 🎉 Success Criteria

Your MCP integration is working correctly if:

✅ All servers can be created, edited, and deleted
✅ Health checks return proper status
✅ Resources can be browsed and read
✅ Tools can be executed with parameters
✅ Results display correctly
✅ Config export works
✅ No console errors in browser or backend
✅ UI is responsive and intuitive

---

## 📝 Next Steps After Testing

Once basic testing is complete, you can:

1. **Create Real MCP Servers:**
   - Connect to actual MCP server implementations
   - Test with production data

2. **Integrate with Chat:**
   - Use `@mcp:resource` syntax in chat (Phase 4)
   - Tool calling from conversations

3. **Install MCP Inspector:**
   - Add debugging capabilities (Phase 3)
   - Monitor MCP protocol traffic

4. **Deploy to Production:**
   - Configure production MCP servers
   - Set up global servers for all users

---

## 🆘 Need Help?

If you encounter issues:

1. Check browser console (F12) for JavaScript errors
2. Check backend logs for Python errors
3. Verify database migration ran successfully
4. Ensure test MCP server is working standalone
5. Review the error messages in toast notifications

Good luck with testing! 🚀
