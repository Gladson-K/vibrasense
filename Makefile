PYTHON ?= python3

.PHONY: test syntax-check lint typecheck test-docker compose-up compose-down fw-check sbom

test:
	$(PYTHON) -m pytest -q

syntax-check:
	$(PYTHON) -m compileall -q software ml tests

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m compileall -q software ml tests

test-docker:
	docker compose run --rm tester

compose-up:
	docker compose up -d mosquitto gateway

compose-down:
	docker compose down

fw-check:
	docker compose --profile firmware run --rm firmware-build

sbom:
	$(PYTHON) -m cyclonedx_py environment -o sbom.json
