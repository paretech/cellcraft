VENV   := venv
PY     := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip
RUFF   := $(VENV)/bin/ruff
MYPY   := $(VENV)/bin/mypy

.DEFAULT_GOAL := help

# ---------------------------------------------------------------------------
# Stamp file: re-runs install whenever pyproject.toml changes.
# ---------------------------------------------------------------------------
$(VENV)/.stamp: pyproject.toml
	python3 -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -e ".[dev]"
	touch $@

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	    awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: $(VENV)/.stamp ## Create the virtual environment and install dependencies

.PHONY: install
install: venv ## Alias for venv (editable install + dev extras)

.PHONY: test
test: venv ## Run the test suite
	$(PY) -m unittest discover -s tests -v

.PHONY: lint
lint: venv ## Check code style with ruff
	$(RUFF) check cellcraft/ tests/

.PHONY: format-check
format-check: venv ## Check formatting without making changes
	$(RUFF) format --check cellcraft/ tests/

.PHONY: typecheck
typecheck: venv ## Run static type checking with mypy
	$(MYPY) cellcraft/

.PHONY: check
check: lint format-check typecheck test ## Run all quality gates

.PHONY: example
example: venv ## Run example_01_patterns.py
	$(PY) examples/example_01_patterns.py

.PHONY: clean
clean: ## Remove the virtual environment and cache directories
	rm -rf $(VENV) .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
