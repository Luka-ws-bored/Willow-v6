# 🛠️ Willow v6 — Configuration Guide

Willow uses a centralized `config.yaml` file in the root directory to control system behavior, active tools, and model order preferences.

---

## 🧾 Sample `config.yaml`

```yaml
active_plugins:
  - prompt_checker
  - bug_buster
  - sql_sorcerer

model_priority:
  - local: lmstudio
  - cloud: openai
  - fallback: claude

features:
  enable_gui: true
  multimodal_support: false
  reverse_proxy_routing: true
  verbose_mode: false

memory:
  enabled: true
  type: vector
  provider: chromadb
```

---

## 🔧 Configuration Options

### `active_plugins`

List of internal tools Willow loads at runtime.
These correspond to folders in `prompts/` or scripts in `agents/`.

### `model_priority`

Defines the fallback order between local and remote models.

* `local`: supports `ollama`, `lmstudio`, or `custom`
* `cloud`: supports `openai`, `claude`, `mistral`, `groq`, etc.
* `fallback`: used if primary providers fail

### `features`

Toggles for GUI, multimodal processing, and other optional features.

### `memory`

Defines how Willow stores session memory or embeddings.

---

## 🧪 Updating Config Live

You can edit the `config.yaml` and rerun `willow.py` to apply changes.

Advanced users can script config changes using a CLI utility (coming soon in v6.1).

---

## 📁 See Also

* [Installation Guide](./installation.md)
* [Prompt Library](./prompt-library.md)
* [API Routing](./api-routing.md) 