# 📜 CHANGELOG — Willow v6

All notable changes to this project will be documented in this file.

This format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
and adheres to [Semantic Versioning](https://semver.org/).

---

## [v6.0.0] - 2025-07-04

### Added

- Complete rewrite of `README.md` with feature-focused breakdown
- Planned support for multimodal I/O (Vision, Audio)
- Modular documentation system setup (to be populated in `/docs`)
- New Prompt Library integration: Bug Buster, SQL Sorcerer, Prompt Checker, etc.
- Improved API key fallback and routing via reverse proxy
- Project structure revamp for scalability

### Changed

- Renamed legacy folders and scripts to follow a cleaner modular naming convention
- Centralized config management in `config.yaml`

### Removed

- Deprecated static prompt blocks in codebase (moved to `/prompts`)

---

## [v6.0.0]

### Added

- Basic GUI frontend (experimental)
- Claude and Groq API compatibility
- Custom skill modules and LLM fallback logic

### Fixed

- Token overflow issues on OpenAI completions
- Runtime errors in local model fallback mode

---

## [v5.0.0] - 2024-11-01

Initial public release.
