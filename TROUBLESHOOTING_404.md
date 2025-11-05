# Fixing the 404 Error on MCP Health Check

## The Problem

When clicking "Health Check" on an MCP server, you see:
```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

## Root Cause

The MCP router wasn't loaded by the backend server. This happens when:
1. ❌ Backend wasn't restarted after adding new code
2. ❌ Database migration didn't run
3. ❌ Import error preventing router from loading

## Solution

### Step 1: Restart Backend Server

**Kill the current backend process:**
```bash
# Find and kill the backend process
pkill -f "open_webui"
# OR
pkill -f "uvicorn"
# OR press Ctrl+C in the terminal running the backend
```

**Start backend fresh:**
```bash
cd backend
python -m open_webui serve
```

**OR:**
```bash
cd backend
uvicorn open_webui.main:app --reload --host 0.0.0.0 --port 8080
```

### Step 2: Verify Migration Ran

Look for this in the startup logs:
```
INFO  [alembic.runtime.migration] Running upgrade a5c220713937 -> mcp_001_initial, Add MCP (Model Context Protocol) tables
```

If you DON'T see this, run migration manually:
```bash
cd backend
alembic upgrade head
```

### Step 3: Verify Router Loaded

Check the startup logs for any errors related to `mcp`:
```bash
# Look for import errors
grep -i "error" backend_logs.txt | grep -i "mcp"

# OR check if routes are registered
curl http://localhost:8080/api/v1/mcp/servers \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 4: Check Backend Logs

When you click "Health Check", watch the backend logs:
```bash
# In the terminal running the backend, you should see:
POST /api/v1/mcp/servers/abc123/health
```

If you DON'T see this request, the backend isn't receiving it (CORS or proxy issue).

If you see:
```
404 Not Found - /api/v1/mcp/servers/abc123/health
```
Then the router isn't loaded.

## Quick Fix Commands

```bash
# 1. Kill backend
pkill -f "open_webui"

# 2. Fix file watchers (if needed)
sudo sysctl fs.inotify.max_user_watches=524288

# 3. Start backend
cd /home/rangarb/badri/Badri-OWUI/backend
python -m open_webui serve

# 4. In another terminal, start frontend
cd /home/rangarb/badri/Badri-OWUI
npm run dev
```

## Verification Steps

### 1. Check if Backend is Running
```bash
curl http://localhost:8080/api/health
```
Should return: `{"status": "ok"}`

### 2. Check if MCP Router is Loaded
```bash
# Get your auth token from browser (F12 → Application → Local Storage → token)
curl http://localhost:8080/api/v1/mcp/servers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Should return: `[]` (empty array) or your servers list

If you get `404`, router isn't loaded.

### 3. Test Health Check API Directly
```bash
# Create a test server first via UI, then:
curl -X POST http://localhost:8080/api/v1/mcp/servers/YOUR_SERVER_ID/health \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

Should return health status.

## Common Issues

### Issue 1: "Module not found" error in backend logs

**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Fix:**
```bash
pip install mcp
```

### Issue 2: "No such table: mcp_server"

**Error:**
```
sqlite3.OperationalError: no such table: mcp_server
```

**Fix:**
```bash
cd backend
alembic upgrade head
# OR delete the database and restart:
rm -f backend/data/webui.db
python -m open_webui serve
```

### Issue 3: Still getting 404 after restart

**Check if router is actually imported in main.py:**
```bash
grep "mcp" backend/open_webui/main.py
```

Should show:
```python
from open_webui.routers import (
    ...
    mcp,  # ← This line should be there
)
...
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])  # ← And this
```

If missing, the code wasn't properly saved/committed.

### Issue 4: CORS Error

**Error in browser console:**
```
Access to fetch at 'http://localhost:8080/api/v1/mcp/...' has been blocked by CORS policy
```

**This means backend IS running and router IS loaded, but CORS is misconfigured.**

**Fix:** Make sure you're accessing frontend and backend on same origin or CORS is properly configured.

## Still Not Working?

### Get Detailed Logs

**1. Check Backend Startup:**
```bash
cd backend
python -m open_webui serve 2>&1 | tee backend.log
```

**2. Look for Errors:**
```bash
grep -i "error\|exception\|traceback" backend.log
```

**3. Check if MCP Tables Exist:**
```bash
sqlite3 backend/data/webui.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mcp%';"
```

Should show:
```
mcp_server
mcp_resource
mcp_tool
```

### Check Frontend API Call

**Open browser DevTools (F12) → Network tab:**
1. Click "Health Check" button
2. Look for request to `/api/v1/mcp/servers/XXX/health`
3. Check the request URL is correct
4. Check the response status

**Expected:**
- Request URL: `http://localhost:8080/api/v1/mcp/servers/abc123/health`
- Method: `POST`
- Status: `200 OK`

**If you see:**
- Status: `404` → Router not loaded (restart backend)
- Status: `401` → Authentication issue (check token)
- Status: `500` → Server error (check backend logs)
- No request at all → Frontend issue (check browser console)

## Nuclear Option: Fresh Start

If nothing works, start fresh:

```bash
# 1. Stop everything
pkill -f "open_webui"
pkill -f "vite"

# 2. Pull latest code
cd /home/rangarb/badri/Badri-OWUI
git pull

# 3. Rebuild
npm install
cd backend
pip install -r requirements.txt

# 4. Clean database (CAUTION: This deletes all data!)
rm -f data/webui.db

# 5. Start fresh
python -m open_webui serve

# 6. In another terminal
cd ..
npm run dev
```

## Need More Help?

**Share these with me:**
1. Backend startup logs (first 50 lines)
2. Error in browser console (F12 → Console)
3. Network request details (F12 → Network → failed request)
4. Output of: `ls -la backend/open_webui/routers/mcp.py`
5. Output of: `ls -la backend/open_webui/models/mcp.py`

I'll help debug further!
