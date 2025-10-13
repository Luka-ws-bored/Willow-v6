.PHONY: run-server install-deps test-api

run-server:
	python -m cmd.willow_server.app

install-deps:
	pip install -r requirements.txt

test-api:
	pytest -q tests/test_api_smoke.py