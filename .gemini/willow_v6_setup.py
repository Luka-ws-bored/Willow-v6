import os

# Step 1: Folder structure
folders = [
    "willow/agents", "willow/pipelines", "willow/configs",
    "willow/prompts", "willow/core", "willow/ui",
    "willow/utils", "willow/test"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "__init__.py"), "w") as f:
        f.write("# Init\n")

# Step 2: Basic config templates
configs = {
    "openai_config.json": {
        "model": "gpt-4",
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY"
    },
    "claude_config.json": {
        "model": "claude-3-sonnet",
        "base_url": "https://api.anthropic.com",
        "key_env": "ANTHROPIC_API_KEY"
    },
    "mistral_config.json": {
        "model": "mistral-small",
        "base_url": "https://api.mistral.ai",
        "key_env": "MISTRAL_API_KEY"
    },
    "local_config.json": {
        "model": "gemma-7b",
        "base_url": "http://localhost:11434",
        "key_env": "LOCAL_MODEL_KEY"
    }
}

for file, content in configs.items():
    with open(f"willow/configs/{file}", "w") as f:
        import json
        json.dump(content, f, indent=4)

# Step 3: Shell script for launching
with open("run_willow.sh", "w") as f:
    f.write("""#!/bin/bash
echo "Launching Willow..."
python willow/ui/cli.py
""")

print("✅ Willow v6 project structure and base configs created.")

# Gemini Prompt (run in terminal or ask Gemini to do it)
# ⬇️ Copy this and ask Gemini to execute
# "Execute willow_v6_setup.py and open willow/ui/cli.py"
