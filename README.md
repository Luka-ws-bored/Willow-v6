# 🌿 Willow v6 — AI Automation Framework (Multimodal Ready)

Willow is your customizable personal AI assistant framework.  
Built for power users, hackers, and indie agents, it bridges local models, cloud APIs, and GUI workflows into one intelligent system.

---

## ✨ Key Features

- 🔁 **Rotating API Proxy Support**: Seamless fallback between OpenAI, Claude, Gemini, Mistral, and more
- 🧠 **Multimodal Architecture**: (Planned) Vision, text, and speech input/output support
- 🖥️ **Local Model Integration**: Connect to LM Studio, Ollama, or other local backends
- 🧩 **Plugin Modules**: Add or disable skills like AutoGPT tools, agents, memory, and more
- 🌐 **Reverse Proxy Ready**: Works with reverse-proxied API keys (like OpenRouter, Groq)
- 📜 **Structured Prompts & Chaining**: Claude-style <thinking> tags, budgeted reasoning, reusable chains
- 🧪 **Experimental Tools**: SQL Sorcerer, Prompt Checker, Bug Buster, Color Mood Mapper, and more

---

## 📦 Installation

> **System Requirements**  
> Python 3.9+  
> Git  
> Node.js (for GUI or agent wrappers)

```bash
git clone https://github.com/Luka-ws-bored/Willow.git
cd Willow
pip install -r requirements.txt
```

(Optional GUI dependencies — coming soon for v6):

```bash
cd gui
npm install
npm run dev
```

---

## 🧠 Getting Started

1. Create your `.env` file and add your API keys:

   ```env
   OPENAI_API_KEY=sk-...
   CLAUDE_API_KEY=...
   ```

2. Run the main agent:

   ```bash
   python willow.py
   ```

3. Use `config.yaml` to toggle features, assign local models, or define custom prompts

---

## 📁 Project Structure

```
Willow/
├── willow.py              # Main orchestrator script
├── config.yaml            # Feature toggles, API keys, model order
├── prompts/               # Modular prompt templates
├── agents/                # Sub-agents (researcher, fixer, translator, etc)
├── utils/                 # Helper functions (IO, tools, chains)
├── docs/                  # Split documentation files (planned in v6)
└── gui/                   # Optional GUI frontend (in progress)
```

---

## 🚧 Roadmap for v6

- [x] Documentation overhaul
- [ ] Multimodal inputs (vision/audio)
- [ ] Dynamic plugin loading
- [ ] Memory system upgrade
- [ ] GUI assistant interface
- [ ] Advanced chaining & reasoning engine

---

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for details on version history.

---

## 🤝 Contributing

Got a feature idea? Want to add support for a new LLM API or local model?
Feel free to fork, submit issues, or reach out via the Discussions tab.

---

## 🧙‍♂️ License

MIT — Use freely, modify fiercely. Credit is cool but not required.

---

## 👤 Author

**BoredPerson**
With guidance from Meliodas

---

> "Let the trees speak. Let the agents rise." 🌲
