# PR: chore: repo scaffolding and contributor docs

## Summary of Actions

This PR implements the initial scaffolding for the Willow repository as part of Phase 0 Day 1 requirements. The following actions were completed:

1. Created the feature branch `feature/willow-scaffold` from `main`
2. Confirmed Ollama endpoint status (currently not running locally)
3. Created the repository layout with directories:
   - `cmd/`, `internal/`, `core/`, `apps/`, `infra/`, `tui/`, `docs/`, `third_party/`
4. Added contributor documentation:
   - `README.md` (skeleton)
   - `CONTRIBUTING.md`
   - `CODE_OF_CONDUCT.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
5. Created placeholder for collected LLM apps in `third_party/llm_apps/collected_20251013115433/`
6. Added Ollama adapter skeleton in `core/llm_adapter.py` (Python-based)
7. Added infrastructure files:
   - `infra/docker-compose.local.yml` (Ollama + Chroma)
   - `infra/scripts/bootstrap_local.sh`
8. Added health check template and ran it successfully
9. Implemented security measures:
   - `.env.example` file
   - `.pre-commit-config.yaml` with detect-secrets
   - `.secrets.baseline` for secret detection

## Ollama Endpoint Confirmation

Ollama is currently not running on the expected endpoint `http://localhost:11434`. No processes were found on ports 11433-11435. 

To start Ollama, users can either:
1. Install Ollama directly and run `ollama serve`
2. Use the provided docker-compose file: `docker-compose -f infra/docker-compose.local.yml up -d`

## Files Added

- `.env` - Contains OLLAMA_URL configuration
- `.env.example` - Example environment variables
- `.github/PULL_REQUEST_TEMPLATE.md` - Standard PR template
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.secrets.baseline` - Detect-secrets baseline
- `CODE_OF_CONDUCT.md` - Community code of conduct
- `CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Project README skeleton
- `core/llm_adapter.py` - Ollama adapter skeleton
- `docs/ollama_endpoint.md` - Ollama endpoint status documentation
- `docs/phase0_migration_report.md` - Health check results
- `infra/docker-compose.local.yml` - Local development services
- `infra/scripts/bootstrap_local.sh` - Local environment bootstrap script
- `TEMPLATES/health_check.py` - Health check template
- `third_party/llm_apps/collected_20251013115433/README.md` - Collected LLM apps placeholder

## How I Tested

1. Ran the health check template to verify core dependencies
2. Verified all new files can be imported/loaded without errors
3. Confirmed directory structure matches requirements
4. Validated Ollama endpoint status through curl commands
5. Tested pre-commit configuration with detect-secrets

## Next Steps

Once this PR is merged, the next steps would be to:
1. Actually start Ollama service locally
2. Implement more comprehensive adapter functionality
3. Add actual LLM applications to the third_party directory
4. Expand the core framework components