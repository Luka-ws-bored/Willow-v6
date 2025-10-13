# Migration mapping: existing backend -> /api/v1

Goal: expose stable endpoints for TUI first; wrap existing handlers/controllers.

1. Existing route: <existing_workspace_route> -> /api/v1/workspaces
   - Handler: return paged workspace list
   - Mapping: if existing returns HTML or template, add JSON wrapper function.

2. Existing route: <existing_items_route> -> /api/v1/workspaces/{id}/items
   - Handler: list items, support ?q= query param + cursor

3. Existing route: <existing_item_detail> -> /api/v1/items/{id}
   - Handler: return full item JSON

4. Existing update route -> PATCH /api/v1/items/{id}
   - Handler: accept partial JSON updates and return updated object

5. Add: POST /api/v1/query -> executes saved/adhoc queries (wrap existing search)

6. Add: POST /api/v1/chat -> call local Ollama adapter (core.llm_adapter.OllamaAdapter)

7. Add: GET /status -> health checks for backend + ollama adapter health


(If Qoder finds route names that differ, update this file.)