# ⚙️ Willow v6 — Installation Guide

This document walks you through installing Willow and all its dependencies.

---

## 🧾 Prerequisites

- Python 3.9 or higher
- Git
- Node.js (for GUI frontend)

To verify:

```bash
python --version
git --version
node -v
```

Install if missing:

- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/)

---

## 📦 Clone and Install Dependencies

```bash
git clone https://github.com/Luka-ws-bored/Willow.git
cd Willow
pip install -r requirements.txt
```

---

## 🧪 Running Willow

Create a `.env` file in the root folder:

```env
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=...
MISTRAL_API_KEY=...
```

Then launch:

```bash
python willow.py
```

---

## 🖥️ GUI (Optional - Experimental)

```bash
cd gui
npm install
npm run dev
```

The GUI is experimental and may change frequently in v6.

---

## ✅ What's Next?

- Customize feature flags in `config.yaml`
- Add skills and models in `agents/` and `prompts/`
- Check `/docs/configuration.md` to tune system behavior
