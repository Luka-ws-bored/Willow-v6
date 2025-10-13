# cmd/willow_server/app.py
"""
FastAPI server that exposes the Willow /api/v1 surface.
- Maps to existing backend functions when present.
- Falls back to simple in-memory stores if not.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import importlib

logger = logging.getLogger("willow")
logging.basicConfig(level=logging.INFO)

API_PREFIX = "/api/v1"
app = FastAPI(title="Willow API", version="1.0.0")

# CORS for local dev TUI if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to import existing modules; fall back to in-memory implementations
def safe_import(module_path: str):
    try:
        return importlib.import_module(module_path)
    except Exception:
        logger.info("Module %s not available; will use fallback.", module_path)
        return None

core_items = safe_import("internal.items") or safe_import("core.items") or None
core_workspaces = safe_import("internal.workspaces") or safe_import("core.workspaces") or None
llm_module = safe_import("core.llm_adapter") or safe_import("core.llm_adapter") or None

# Simple in-memory stores (fallback)
IN_MEM = {
    "workspaces": [
        {"id": "ws_1", "name": "Personal", "description": "Personal workspace"}
    ],
    "items": {
        "ws_1": [
            {"id": "itm_1", "title": "Hello world", "status": "open", "body": "Example body", "updated_at": None}
        ]
    },
}

# Pydantic models for API
class TokenRequest(BaseModel):
    api_key: str

class Workspace(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class ItemSummary(BaseModel):
    id: str
    title: str
    status: Optional[str] = None
    updated_at: Optional[str] = None

class ItemDetail(BaseModel):
    id: str
    title: str
    body: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    updated_at: Optional[str] = None

class QueryRequest(BaseModel):
    q: Optional[str] = None
    limit: Optional[int] = 10

class ChatRequest(BaseModel):
    model: Optional[str] = "llama2"
    messages: List[Dict[str, Any]]

# Health endpoint
@app.get("/status")
def status():
    ollama_ok = False
    try:
        if llm_module and hasattr(llm_module, "OllamaAdapter"):
            client = llm_module.OllamaAdapter()
            # adapter should expose a .health(ctx) or .health() method — try both
            health = None
            try:
                health = client.health()
            except TypeError:
                # maybe expects no args or uses httpx internally
                health = client.health()
            ollama_ok = health is None or health is True
        else:
            logger.info("LLM adapter not present; reporting ollama_ok=False")
    except Exception as e:
        logger.exception("Ollama health check failed: %s", e)
        ollama_ok = False

    return {"server": "ok", "ollama": "ok" if ollama_ok else "unavailable"}

# Auth token exchange (dev-only)
@app.post(API_PREFIX + "/auth/token")
def auth_token(req: TokenRequest):
    # Local dev: accept any api_key and return a dummy token
    # In prod, integrate with your auth store
    return {"token": f"dev-token-for-{req.api_key}", "expires_at": None}

# Workspaces: list
@app.get(API_PREFIX + "/workspaces", response_model=List[Workspace])
def list_workspaces(page: int = Query(1), per_page: int = Query(50)):
    if core_workspaces and hasattr(core_workspaces, "list_workspaces"):
        return core_workspaces.list_workspaces(page=page, per_page=per_page)
    # fallback
    return IN_MEM["workspaces"]

# Items in workspace
@app.get(API_PREFIX + "/workspaces/{workspace_id}/items", response_model=List[ItemSummary])
def list_workspace_items(workspace_id: str = Path(...), q: Optional[str] = None, cursor: Optional[str] = None, limit: int = Query(50)):
    if core_items and hasattr(core_items, "list_items_by_workspace"):
        return core_items.list_items_by_workspace(workspace_id, q=q, cursor=cursor, limit=limit)
    return IN_MEM["items"].get(workspace_id, [])

# Item detail
@app.get(API_PREFIX + "/items/{item_id}", response_model=ItemDetail)
def get_item(item_id: str = Path(...)):
    # Try existing module
    if core_items and hasattr(core_items, "get_item"):
        item = core_items.get_item(item_id)
        if item:
            return item
        raise HTTPException(status_code=404, detail="item not found")
    # fallback search
    for ws_items in IN_MEM["items"].values():
        for it in ws_items:
            if it["id"] == item_id:
                return it
    raise HTTPException(status_code=404, detail="item not found")

# Patch/update item
@app.patch(API_PREFIX + "/items/{item_id}", response_model=ItemDetail)
def patch_item(item_id: str, payload: Dict = Body(...)):
    if core_items and hasattr(core_items, "update_item"):
        updated = core_items.update_item(item_id, payload)
        return updated
    # fallback: mutate in-memory
    for ws, ws_items in IN_MEM["items"].items():
        for it in ws_items:
            if it["id"] == item_id:
                it.update(payload)
                return it
    raise HTTPException(status_code=404, detail="item not found")

# Query endpoint
@app.post(API_PREFIX + "/query")
def run_query(req: QueryRequest):
    # If existing search API exists, call it
    search_mod = safe_import("core.search") or safe_import("internal.search")
    if search_mod and hasattr(search_mod, "run_query"):
        return search_mod.run_query(req.q or "", limit=req.limit)
    # fallback: simple fuzzy filter on titles
    results = []
    q = (req.q or "").lower()
    for ws_items in IN_MEM["items"].values():
        for it in ws_items:
            if q in it.get("title", "").lower() or q in it.get("body","").lower():
                results.append(it)
                if len(results) >= (req.limit or 10):
                    break
    return {"results": results}

# Chat / LLM endpoint
@app.post(API_PREFIX + "/chat")
def chat(req: ChatRequest):
    if not llm_module or not hasattr(llm_module, "OllamaAdapter"):
        raise HTTPException(status_code=503, detail="LLM adapter not available")
    try:
        client = llm_module.OllamaAdapter()
        # Expect the adapter to implement chat(messages=..., model=...)
        # support sync or async methods
        if hasattr(client, "chat"):
            # some adapters return dict or raw text
            resp = client.chat(messages=req.messages, model=req.model)
            return {"output": resp}
        elif hasattr(client, "Generate"):
            resp = client.Generate(model=req.model, prompt=req.messages)
            return {"output": resp}
        else:
            raise HTTPException(status_code=500, detail="adapter missing expected interface")
    except Exception as e:
        logger.exception("LLM call failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# Root
@app.get("/")
def root():
    return {"message": "Willow API up. See /status and /docs"}

# If run as script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cmd.willow_server.app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=True)