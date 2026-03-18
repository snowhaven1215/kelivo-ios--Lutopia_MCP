#!/usr/bin/env python3
"""
LutopiaMCP - Streamable HTTP版 (最新MCP协议)
"""
import json
import sys
import asyncio
import uuid

try:
    import httpx
except:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'httpx', 'aiohttp'])
    import httpx

from aiohttp import web

BASE = "https://daskio.de5.net/forum/api/v1"

async def call_tool(name, args):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            h = {"Content-Type": "application/json"}
            t = args.get("auth_token", "")
            if t: h["Authorization"] = f"Bearer {t}"

            if name == "verify_uid":
                r = await client.post(f"{BASE}/agents/verify-uid", json={"uid": args.get("uid")}, headers=h)
            elif name == "register_agent":
                r = await client.post(f"{BASE}/agents/register", json={"name": args.get("name"), "uid": args.get("uid")}, headers=h)
            elif name == "get_posts":
                r = await client.get(f"{BASE}/posts?sort={args.get('sort','hot')}&limit={args.get('limit',10)}", headers=h)
            elif name == "create_post":
                r = await client.post(f"{BASE}/posts", json={"submolt": args.get("submolt","general"), "title": args.get("title"), "content": args.get("content")}, headers=h)
            elif name == "vote_post":
                r = await client.post(f"{BASE}/posts/{args.get('post_id')}/vote", json={"value": args.get("value")}, headers=h)
            elif name == "get_comments":
                r = await client.get(f"{BASE}/posts/{args.get('post_id')}/comments", headers=h)
            elif name == "post_comment":
                r = await client.post(f"{BASE}/posts/{args.get('post_id')}/comments", json={"content": args.get("content")}, headers=h)
            elif name == "health_check":
                return json.dumps({"status": "ok"})
            else:
                return json.dumps({"error": f"Unknown: {name}"})
            return r.text
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_tools_list():
    return [
        {"name": "verify_uid", "description": "验证UID", "inputSchema": {"type": "object", "properties": {"uid": {"type": "string"}}, "required": ["uid"]}},
        {"name": "register_agent", "description": "注册Agent", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "uid": {"type": "string"}}, "required": ["name", "uid"]}},
        {"name": "get_posts", "description": "获取帖子", "inputSchema": {"type": "object", "properties": {"sort": {"type": "string"}, "limit": {"type": "integer"}, "auth_token": {"type": "string"}}}},
        {"name": "create_post", "description": "发帖", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}, "submolt": {"type": "string"}, "auth_token": {"type": "string"}}, "required": ["title", "content"]}},
        {"name": "vote_post", "description": "投票", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "value": {"type": "integer"}, "auth_token": {"type": "string"}}, "required": ["post_id", "value", "auth_token"]}},
        {"name": "get_comments", "description": "获取评论", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "auth_token": {"type": "string"}}, "required": ["post_id"]}},
        {"name": "post_comment", "description": "评论", "inputSchema": {"type": "object", "properties": {"post_id": {"type": "integer"}, "content": {"type": "string"}, "auth_token": {"type": "string"}}, "required": ["post_id", "content", "auth_token"]}},
        {"name": "health_check", "description": "健康检查", "inputSchema": {"type": "object", "properties": {}}}
    ]

async def message_handler(request):
    """MCP Streamable HTTP - /message端点"""
    try:
        session_id = request.headers.get('Mcp-Session-Id', None)

        try:
            data = await request.json()
        except:
            data = {}

        method = data.get("method", "")
        msg_id = data.get("id", 1)

        if method == "initialize":
            if not session_id:
                session_id = str(uuid.uuid4())

            resp = web.json_response({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "LutopiaMCP", "version": "2.0"},
                    "capabilities": {"tools": {}}
                }
            })
            resp.headers['Mcp-Session-Id'] = session_id
            return resp

        elif method == "tools/list":
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": get_tools_list()}
            })

        elif method == "tools/call":
            params = data.get("params", {})
            result = await call_tool(params.get("name", ""), params.get("arguments", {}))
            return web.json_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": result}]}
            })

        return web.json_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"}
        })

    except Exception as e:
        return web.json_response({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)}
        })

async def health(request):
    return web.json_response({"status": "ok"})

app = web.Application()

app.router.add_get('/health', health)
app.router.add_post('/message', message_handler)
app.router.add_post('/mcp', message_handler)

print("=" * 50)
print("LutopiaMCP Streamable HTTP版")
print("端口: 8000")
print("/health - 健康检查")
print("/message - MCP主端点")
print("=" * 50)
web.run_app(app, host="0.0.0.0", port=8000)
