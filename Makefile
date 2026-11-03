.PHONY: help install test eval safety api ui load data-validation lint all clean

# ──── Default ────────────────────────────────────
help: ## Show this help message
	@echo.
	@echo  Micropatient AI Test Suite — Available Commands
	@echo  ═══════════════════════════════════════════════
	@echo.
	@echo  install          Install all dependencies
	@echo  test             Run all tests (evals + safety + api + ui + data)
	@echo  eval             Run LLM evaluation tests (DeepEval + Ragas)
	@echo  safety           Run AI safety tests
	@echo  api              Run REST API tests
	@echo  ui               Run Playwright UI tests
	@echo  load             Run Locust load tests (headless, 10 users, 60s)
	@echo  data-validation  Run SQL/Athena data validation tests
	@echo  promptfoo        Run promptfoo evaluation matrix
	@echo  lint             Run ruff linter
	@echo  all              Run everything (lint + test + load)
	@echo  clean            Remove reports and caches
	@echo.

# ──── Setup ──────────────────────────────────────
install: ## Install all project dependencies
	pip install -e ".[dev]"
	playwright install chromium

# ──── Test Suites ────────────────────────────────
test: ## Run all tests except load
	pytest evals/ safety/ tests/ --tb=short -v

eval: ## Run LLM evaluation tests only
	pytest evals/ -m llm_eval --tb=short -v

safety: ## Run AI safety tests only
	pytest safety/ -m safety --tb=short -v

api: ## Run REST API tests only
	pytest tests/api/ -m api --tb=short -v

ui: ## Run Playwright UI tests (headless)
	pytest tests/ui/ -m ui --headed=false --tb=short -v

load: ## Run Locust load tests (headless)
	locust -f loadtests/locustfile.py --headless -u 10 -r 2 --run-time 60s --host http://localhost:8000

data-validation: ## Run SQL/Athena data validation tests
	pytest tests/data_validation/ -m data_validation --tb=short -v

# ──── Promptfoo ──────────────────────────────────
promptfoo: ## Run promptfoo evaluation matrix
	cd promptfoo && npx promptfoo@latest eval

promptfoo-view: ## Open promptfoo results dashboard
	cd promptfoo && npx promptfoo@latest view

# ──── Quality ────────────────────────────────────
lint: ## Run ruff linter
	ruff check . --fix

all: lint test load ## Run everything

# ──── Cleanup ────────────────────────────────────
clean: ## Remove generated reports and caches
	rmdir /s /q reports 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q .ruff_cache 2>nul || true
	rmdir /s /q __pycache__ 2>nul || true
	mkdir reports
