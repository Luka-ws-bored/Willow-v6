# tests/test_api_smoke.py
import os
import requests

BASE = os.environ.get("WILLOW_API", "http://localhost:8080")

def test_status():
    r = requests.get(f"{BASE}/status")
    assert r.status_code == 200
    j = r.json()
    assert "server" in j

def test_list_workspaces():
    r = requests.get(f"{BASE}/api/v1/workspaces")
    assert r.status_code == 200