# apps/starter_agents/ai_travel_agent/app.py
import os
import json
from core.llm_adapter import OllamaAdapter

def main():
    adapter = OllamaAdapter()
    messages = [
        {"role":"user","content":"Plan a 3-day itinerary for Lagos, Nigeria for a tech conference attendee."}
    ]
    resp = adapter.chat(messages=messages)
    print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    main()