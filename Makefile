PYTHON ?= python3
.PHONY: install download db-start db-stop pipeline test
install:
	$(PYTHON) -m pip install -r requirements-dev.txt
download:
	./scripts/download_manual.sh
db-start:
	./scripts/start_local_postgres.sh
db-stop:
	./scripts/stop_local_postgres.sh
pipeline:
	PYTHONPATH=src $(PYTHON) pipelines/run_pipeline.py
test:
	PYTHONPATH=src $(PYTHON) -m pytest -q
