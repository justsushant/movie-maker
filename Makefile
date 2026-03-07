.PHONY: setup install run test test-unit test-integration test-stress test-all clean clean-test help

PYTHON ?= python3.10
VENV   := .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: ## Install dependencies into existing venv
	$(PIP) install -r requirements.txt

run: ## Run the full pipeline (TTS → video)
	$(PY) main.py

test: ## Run all tests (unit + integration + stress)
	@echo "Running full test suite..."
	PYTHONPATH=. $(PYTEST) tests/ -v

test-unit: ## Run unit tests only (fast, no TTS generation)
	@echo "Running unit tests..."
	PYTHONPATH=. $(PYTEST) tests/ -v -k "Unit or test_tts_config or test_video_config or test_io_config or test_punctuation or test_sentence or test_kokoro or test_tts_pipeline or test_api_backward"

test-integration: ## Run integration tests (includes TTS generation)
	@echo "Running integration tests..."
	PYTHONPATH=. $(PYTEST) tests/test_library_api.py -v -k "Integration or Comparison"

test-stress: ## Run subtitle stress test suite
	@echo "Running stress tests..."
	PYTHONPATH=. $(PYTEST) tests/test_subtitle_stress.py -v

test-all: ## Run all tests with detailed output
	@echo "Running full test suite with detailed output..."
	PYTHONPATH=. $(PYTEST) tests/ -v --tb=short

clean: ## Remove all generated run outputs
	rm -rf output/
	@echo "Cleaned output/"

clean-test: ## Remove test output directories only
	rm -rf output/test/
	@echo "Cleaned test outputs"
