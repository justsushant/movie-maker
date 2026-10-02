.PHONY: setup install check check-env run demo test test-unit test-integration test-stress test-all clean clean-test help

PYTHON ?= python3
VENV   ?= .venv
PY     := $(VENV)/bin/python
PIP    := $(PY) -m pip
PYTEST := $(VENV)/bin/pytest

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv and install dependencies
	$(PYTHON) -c 'import sys; sys.exit("Python 3.10 or newer is required (Python 3.12 recommended).") if sys.version_info < (3, 10) else None'
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

check-env:
	@test -x "$(PY)" || { echo "Project environment missing. Run: make setup"; exit 1; }

install: check-env ## Install dependencies into existing venv
	$(PIP) install -r requirements.txt

check: check-env ## Check dependency imports and the bundled FFmpeg executable
	$(PIP) check
	$(PY) -c 'from api.library import generate_video_from_text; import cv2, librosa, imageio_ffmpeg; import subprocess; subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-version"], check=True, stdout=subprocess.DEVNULL); print("Python dependencies and FFmpeg are ready.")'

run: check-env ## Run the full pipeline (TTS → video)
	$(PY) main.py

demo: check-env ## Render the vertical wolves demo with the project environment
	$(PY) examples/engagement_max_demo.py

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
