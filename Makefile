.PHONY: setup install run clean help

PYTHON ?= python3.10
VENV   := .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: ## Install dependencies into existing venv
	$(PIP) install -r requirements.txt

run: ## Run the full pipeline (TTS → video)
	$(PY) main.py

clean: ## Remove all generated run outputs
	rm -rf output/
	@echo "Cleaned output/"
