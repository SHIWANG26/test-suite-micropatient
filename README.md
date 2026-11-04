# 🧪 AI Quality & Test Automation Suite — Micropatient

> **Production-grade Python/Pytest framework** for comprehensive quality assurance of the Micropatient healthcare AI platform — covering LLM evaluation, AI safety, UI automation, API testing, load testing, data validation, and CI/CD quality gates.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/tested%20with-pytest-green.svg)](https://docs.pytest.org/)
[![DeepEval](https://img.shields.io/badge/LLM%20eval-DeepEval-purple.svg)](https://deepeval.com/)
[![Playwright](https://img.shields.io/badge/UI%20tests-Playwright-orange.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Test Layers](#test-layers)
  - [Layer 1: LLM Evaluation (DeepEval + Ragas)](#layer-1-llm-evaluation)
  - [Layer 2: Prompt Testing (promptfoo + LangSmith)](#layer-2-prompt-testing)
  - [Layer 3: AI Safety Tests](#layer-3-ai-safety-tests)
  - [Layer 4: UI Automation (Playwright)](#layer-4-ui-automation)
  - [Layer 5: API Testing (Pytest + Requests)](#layer-5-api-testing)
  - [Layer 6: Load Testing (Locust)](#layer-6-load-testing)
  - [Layer 7: Data Validation (SQL / AWS Athena)](#layer-7-data-validation)
- [CI/CD Pipeline](#cicd-pipeline)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Monitoring](#monitoring)
- [Contributing](#contributing)

---

## Overview

**Micropatient** is a healthcare AI platform that uses **RAG (Retrieval-Augmented Generation)** to answer patient queries by retrieving relevant medical documents and generating grounded responses. This repository contains the **complete test automation suite** that ensures quality, safety, and reliability across every layer of the system.

### Key Capabilities

- ✅ **Automated LLM evaluation** — Scores RAG answers for accuracy, groundedness, relevance, and refusal behavior using a curated golden dataset
- ✅ **Hallucination tracking** — Monitors hallucination rate per release and flags regressions before deployment
- ✅ **Multi-turn prompt testing** — Validates conversations, tool-calling, and failure recovery with metric thresholds (not simple pass/fail)
- ✅ **AI safety testing** — Prompt injection, jailbreak, PII leakage, and blocked topic enforcement
- ✅ **Reusable Pytest framework** — Page Object pattern for Playwright web flows, Swagger-driven REST API tests, and Locust load tests
- ✅ **Data pipeline validation** — SQL queries against AWS Athena to verify data integrity, freshness, and schema compliance
- ✅ **Full CI/CD integration** — Quality gates in GitHub Actions that block deployment on failures

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GitHub Actions CI/CD                              │
│                                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐   │
│   │LLM Eval │  │ Safety  │  │API Test │  │UI Test  │  │Load Test     │   │
│   │  Gate   │  │  Gate   │  │  Gate   │  │  Gate   │  │  Gate        │   │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬───────┘   │
│        │            │            │            │              │             │
│   ┌────▼────────────▼────────────▼────────────▼──────────────▼──────────┐  │
│   │                     Quality Gate Aggregator                         │  │
│   │               (All gates must pass for deployment)                  │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Test Layers                                    │
│                                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ Layer 1: LLM    │  │ Layer 2: Prompt  │  │ Layer 3: AI Safety      │   │
│  │ DeepEval + Ragas│  │ promptfoo +      │  │ Injection, Jailbreak,   │   │
│  │ Golden Dataset  │  │ LangSmith Traces │  │ PII, Blocked Topics     │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────────────┘   │
│                                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │ Layer 4: UI     │  │ Layer 5: API     │  │ Layer 6: Load           │   │
│  │ Playwright POM  │  │ Pytest+Requests  │  │ Locust Scenarios        │   │
│  │ Web Flows       │  │ Contract Tests   │  │ Stress & Performance    │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Layer 7: Data Validation — SQL / AWS Athena                          │   │
│  │ Pipeline integrity, schema compliance, freshness monitoring          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Monitoring: CloudWatch Dashboards, Latency & Cost Tracking           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.11+ |
| **Test Framework** | Pytest, pytest-xdist, pytest-html |
| **LLM Evaluation** | DeepEval, Ragas, LangSmith |
| **Prompt Testing** | promptfoo |
| **AI Safety** | Custom Pytest + regex pattern matching |
| **UI Automation** | Playwright (Page Object Model) |
| **API Testing** | Requests, JSONSchema, Pydantic |
| **Load Testing** | Locust |
| **Data Validation** | SQL, AWS Athena (pyathena) |
| **Cloud** | AWS (Athena, CloudWatch, S3) |
| **CI/CD** | GitHub Actions |
| **Config** | Pydantic Settings, YAML, dotenv |
| **Linting** | Ruff |

---

## Project Structure

```
micropatient-ai-test-suite/
│
├── .github/workflows/          # CI/CD pipeline definitions
│   ├── full-pipeline.yml       #   Master orchestrator (all gates)
│   ├── llm-eval-gate.yml       #   LLM evaluation quality gate
│   ├── safety-gate.yml         #   AI safety test gate
│   ├── api-test-gate.yml       #   REST API test gate
│   ├── ui-test-gate.yml        #   Playwright UI test gate
│   └── load-test-gate.yml      #   Locust load test gate
│
├── config/                     # Centralized configuration
│   ├── settings.py             #   Pydantic-based settings (env vars)
│   ├── environments.py         #   Dev/staging/prod profiles
│   └── thresholds.yaml         #   Metric thresholds for all layers
│
├── data/                       # Test datasets
│   ├── golden_dataset/         #   Curated RAG evaluation data
│   │   ├── rag_test_cases.json #     15 golden Q&A test cases
│   │   └── multi_turn_conversations.json
│   ├── safety/                 #   AI safety attack vectors
│   │   ├── prompt_injections.json  # 12 injection attacks
│   │   ├── jailbreak_attempts.json # 8 jailbreak strategies
│   │   ├── pii_samples.json        # PII/PHI leakage tests
│   │   └── blocked_topics.json     # 8 forbidden topics
│   ├── api/                    #   API test payloads
│   └── load/                   #   Load test user profiles
│
├── src/                        # Shared source code
│   ├── client/                 #   API wrappers
│   │   ├── micropatient_api.py #     REST API client
│   │   ├── llm_client.py       #     LLM interaction client
│   │   └── athena_client.py    #     AWS Athena SQL client
│   └── utils/                  #   Utilities
│       ├── data_loader.py      #     Dataset loading helpers
│       ├── metrics_tracker.py  #     Hallucination regression tracker
│       └── report_generator.py #     HTML/JSON report generation
│
├── evals/                      # LLM Evaluation Suite
│   ├── test_rag_accuracy.py    #   RAG answer accuracy (DeepEval)
│   ├── test_groundedness.py    #   Faithfulness / groundedness
│   ├── test_relevance.py       #   Answer relevance scoring
│   ├── test_refusal_behavior.py#   Proper refusal detection
│   ├── test_hallucination_tracking.py # Regression tracking
│   └── ragas_batch_eval.py     #   Ragas batch evaluation script
│
├── promptfoo/                  # Prompt Testing (promptfoo)
│   ├── promptfooconfig.yaml    #   Evaluation matrix config
│   ├── prompts/                #   Prompt templates
│   ├── providers/              #   Custom Python provider
│   └── tests/                  #   Multi-turn, tool-calling, failure YAML
│
├── safety/                     # AI Safety Tests
│   ├── test_prompt_injection.py#   12 injection attack vectors
│   ├── test_jailbreak.py       #   8 jailbreak strategies
│   ├── test_pii_leakage.py     #   PII/PHI leakage (HIPAA)
│   └── test_blocked_topics.py  #   Blocked medical topics
│
├── tests/                      # Functional Tests
│   ├── api/                    #   REST API contract tests
│   │   ├── test_patient_api.py #     Patient CRUD
│   │   ├── test_chat_api.py    #     Chat/conversation endpoints
│   │   ├── test_auth_api.py    #     Authentication flows
│   │   └── test_document_api.py#     Document ingestion
│   ├── ui/                     #   Playwright UI tests
│   │   ├── pages/              #     Page Objects (POM)
│   │   │   ├── base_page.py    #       Base page (shared actions)
│   │   │   ├── login_page.py   #       Login page object
│   │   │   ├── dashboard_page.py#      Dashboard page object
│   │   │   ├── chat_page.py    #       Chat interface page object
│   │   │   └── patient_portal_page.py# Patient portal page object
│   │   ├── test_login_flow.py  #     Login E2E tests
│   │   ├── test_chat_flow.py   #     Chat interaction tests
│   │   └── test_dashboard_flow.py#   Dashboard validation
│   └── data_validation/        #   SQL/Athena validation
│       ├── test_pipeline_integrity.py # Data pipeline checks
│       └── test_schema_validation.py  # Schema conformance
│
├── loadtests/                  # Load Testing (Locust)
│   ├── locustfile.py           #   Main entry point
│   ├── scenarios/              #   User behavior modules
│   │   ├── patient_browsing.py #     Patient portal (20% traffic)
│   │   ├── chat_conversation.py#     AI chat (50% traffic)
│   │   └── api_stress.py       #     API CRUD (30% traffic)
│   └── common/                 #   Shared utilities
│       └── auth.py             #     Token caching for load users
│
├── monitoring/                 # Observability
│   ├── cloudwatch_dashboard.json#  CloudWatch dashboard config
│   └── latency_cost_tracker.py  #  Latency & LLM cost monitoring
│
├── reports/                    # Generated test reports (gitignored)
├── conftest.py                 # Root pytest fixtures
├── pyproject.toml              # Dependencies & project metadata
├── pytest.ini                  # Pytest configuration
├── Makefile                    # Convenience commands
├── .env.example                # Environment variable template
└── .gitignore
```

---

## Database Design

The test suite validates data flowing through these Micropatient database schemas via AWS Athena queries:

```
┌──────────────────────────┐      ┌───────────────────────────┐
│       patients           │      │      conversations        │
├──────────────────────────┤      ├───────────────────────────┤
│ patient_id    PK         │─────▶│ conversation_id  PK       │
│ first_name               │      │ patient_id       FK       │
│ last_name                │      │ started_at                │
│ date_of_birth            │      │ ended_at                  │
│ email                    │      │ status                    │
│ phone                    │      │ total_tokens              │
│ created_at               │      │ total_cost_usd            │
│ updated_at               │      │ model_version             │
└──────────┬───────────────┘      └────────────┬──────────────┘
           │                                    │
           │    ┌──────────────────────────┐    │
           │    │       messages            │    │
           │    ├──────────────────────────┤    │
           │    │ message_id      PK       │    │
           │    │ conversation_id FK  ◀────┘    │
           │    │ role (user/ai/system)    │
           │    │ content                  │
           │    │ tokens_used              │
           │    │ latency_ms               │
           │    │ model_used               │
           │    │ created_at               │
           │    └──────────────────────────┘
           │
           │    ┌──────────────────────────┐
           │    │  medical_documents       │
           │    ├──────────────────────────┤
           └───▶│ document_id     PK       │
                │ patient_id      FK       │
                │ document_type            │
                │ content                  │
                │ embedding_id             │
                │ s3_path                  │
                │ ingested_at              │
                │ chunk_count              │
                └──────────────────────────┘

┌──────────────────────────┐      ┌───────────────────────────┐
│    retrieval_logs        │      │     eval_results          │
├──────────────────────────┤      ├───────────────────────────┤
│ log_id           PK      │      │ eval_id          PK       │
│ message_id       FK      │      │ run_id                    │
│ document_id      FK      │      │ test_case_id              │
│ similarity_score         │      │ metric_name               │
│ rank                     │      │ score                     │
│ retrieved_at             │      │ threshold                 │
└──────────────────────────┘      │ passed                    │
                                  │ model_version             │
                                  │ commit_sha                │
                                  │ evaluated_at              │
                                  └───────────────────────────┘
```

> **Note**: The `eval_results` table is unique to this test suite — it stores historical evaluation scores for tracking hallucination rate regressions across releases.

---

## Test Layers

### Layer 1: LLM Evaluation

**Tools**: DeepEval, Ragas | **Location**: `evals/`

Built automated LLM evaluation suites scoring RAG answers against a **curated golden dataset of 15 test cases** spanning 5 medical categories:

| Metric | Tool | Threshold | Description |
|--------|------|-----------|-------------|
| Faithfulness | DeepEval | ≥ 0.80 | Answer grounded in retrieval context |
| Answer Relevancy | DeepEval/Ragas | ≥ 0.75 | Answer addresses the question asked |
| Context Precision | Ragas | ≥ 0.70 | Retrieved context is relevant |
| Context Recall | Ragas | ≥ 0.70 | Relevant context was retrieved |
| Hallucination Rate | Custom | ≤ 0.15 | % of fabricated content |

**Hallucination Tracking**: Each CI run writes scores to `eval_results` and compares against the previous release. A >2% increase in hallucination rate triggers a regression warning.

```bash
pytest evals/ -m llm_eval -v          # Run DeepEval tests
python evals/ragas_batch_eval.py       # Run Ragas batch evaluation
```

---

### Layer 2: Prompt Testing

**Tools**: promptfoo, LangSmith | **Location**: `promptfoo/`

Wrote promptfoo test cases and LangSmith traces for:

- **Multi-turn conversations** — Patient-doctor dialogue sequences with context retention
- **Tool-calling validation** — Appointment booking, prescription lookup, insurance verification
- **Failure recovery** — Graceful handling of service unavailability, invalid IDs, timeouts
- **Non-deterministic outputs** — Uses `llm-rubric`, `similar`, `latency`, `contains` assertions with metric thresholds rather than simple pass/fail

```bash
cd promptfoo && npx promptfoo@latest eval         # Run evaluation matrix
cd promptfoo && npx promptfoo@latest view          # Open results dashboard
```

---

### Layer 3: AI Safety Tests

**Location**: `safety/`

Created AI safety tests converted into permanent regression tests:

| Category | Test Cases | Severity | Tolerance |
|----------|-----------|----------|-----------|
| Prompt Injection | 12 attack vectors | Critical | Zero |
| Jailbreak Resistance | 8 strategies (DAN, roleplay, dev mode) | Critical | Zero |
| PII Leakage | 8 PHI/PII extraction attempts | Critical | Zero |
| Blocked Topics | 8 forbidden topics (self-harm, off-label) | Critical | Zero |

```bash
pytest safety/ -m safety -v            # Run all safety tests
```

---

### Layer 4: UI Automation

**Tools**: Playwright, Page Object Model | **Location**: `tests/ui/`

Built a reusable Playwright framework with **Page Object pattern**:

| Page Object | Responsibilities |
|-------------|-----------------|
| `BasePage` | Common actions: navigate, click, fill, wait, screenshot |
| `LoginPage` | Authentication form, login workflows, error validation |
| `DashboardPage` | Patient list, stats widget, search, navigation |
| `ChatPage` | Message input, AI responses, multi-turn, feedback |
| `PatientPortalPage` | Appointments, documents, profile management |

```bash
pytest tests/ui/ -m ui -v              # Run headless
pytest tests/ui/ -m ui --headed        # Run with visible browser
```

---

### Layer 5: API Testing

**Tools**: Pytest, Requests, JSONSchema | **Location**: `tests/api/`

Swagger/OpenAPI-driven REST API contract tests:

- **Patient API** — CRUD operations, validation, error contracts
- **Chat API** — Message send/receive, conversation management
- **Auth API** — JWT login/logout, token lifecycle, expired tokens
- **Document API** — Upload, retrieval, type validation

```bash
pytest tests/api/ -m api -v            # Run API tests
```

---

### Layer 6: Load Testing

**Tools**: Locust | **Location**: `loadtests/`

Three scenario classes with weighted traffic distribution:

| Scenario | Weight | Pattern | Key Metrics |
|----------|--------|---------|-------------|
| Patient Browsing | 20% | Read-heavy portal browsing | Throughput |
| Chat Conversation | 50% | AI chat message flow | P95 latency < 2s |
| API Stress | 30% | CRUD + document operations | Error rate < 1% |

```bash
# Headless (CI)
locust -f loadtests/locustfile.py --headless -u 100 -r 10 --run-time 5m

# Web UI
locust -f loadtests/locustfile.py  # Open http://localhost:8089
```

---

### Layer 7: Data Validation

**Tools**: SQL, AWS Athena (pyathena) | **Location**: `tests/data_validation/`

Validated pipeline data with SQL queries:

- **Pipeline integrity** — Row counts, null rate checks, duplicate detection
- **Schema validation** — Column types, FK consistency, enum values
- **Data freshness** — Staleness monitoring (< 24h threshold)
- **Latency monitoring** — P50/P95/P99 from message latency data
- **Cost tracking** — Average conversation cost vs budget

```bash
pytest tests/data_validation/ -m data_validation -v
```

---

## CI/CD Pipeline

All tests run as **quality gates in GitHub Actions** that block deployment on failures:

```
┌──────────────┐
│    Lint      │  ← Ruff code quality check
└──────┬───────┘
       │
       ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  LLM Eval   │  │   Safety     │  │  API Tests   │  │ Data Valid.  │
│  (parallel) │  │  (parallel)  │  │  (parallel)  │  │  (parallel)  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       └────────────┬────┴────────┬────────┘                 │
                    ▼             │                           │
              ┌──────────────┐   │                           │
              │   UI Tests   │   │                           │
              └──────┬───────┘   │                           │
                     │           │                           │
                     ▼           ▼                           ▼
              ┌──────────────────────────────────────────────────┐
              │            ✅ Quality Gate Decision               │
              │       (All gates must pass for deployment)       │
              └──────────────────────────────────────────────────┘
```

**Workflow files**: `.github/workflows/`

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `full-pipeline.yml` | Push to `main` / PR | Master orchestrator |
| `llm-eval-gate.yml` | Changes in `evals/`, `data/golden_dataset/` | LLM evaluation |
| `safety-gate.yml` | Changes in `safety/`, `data/safety/` | AI safety |
| `api-test-gate.yml` | Changes in `tests/api/`, `src/client/` | API contracts |
| `ui-test-gate.yml` | Changes in `tests/ui/` | Playwright UI |
| `load-test-gate.yml` | Push to `main` / manual dispatch | Performance |

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for promptfoo)
- **Git**

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/micropatient-ai-test-suite.git
cd micropatient-ai-test-suite

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Install Playwright browsers
playwright install chromium

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional for mock mode)
```

### Quick Start

```bash
# Run all tests (mock mode — no API keys needed)
pytest evals/ safety/ tests/ -v

# Run a specific test suite
pytest evals/ -m llm_eval -v          # LLM evaluation
pytest safety/ -m safety -v            # AI safety
pytest tests/api/ -m api -v            # API tests
pytest tests/data_validation/ -v       # Data validation
```

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `MICROPATIENT_BASE_URL` | Yes | API server URL |
| `OPENAI_API_KEY` | For live eval | OpenAI API key for LLM-as-judge |
| `LANGSMITH_API_KEY` | Optional | LangSmith tracing |
| `DEEPEVAL_API_KEY` | Optional | Confident AI dashboard |
| `AWS_REGION` | For live data | AWS region for Athena |

### Metric Thresholds

All thresholds are centralized in `config/thresholds.yaml`:

```yaml
llm_evaluation:
  faithfulness: 0.80
  answer_relevancy: 0.75
  hallucination_rate: 0.15    # Maximum allowed (lower is better)

safety:
  prompt_injection_resistance: 0.95
  pii_leakage_prevention: 1.00   # Zero tolerance

api:
  latency_p95_ms: 2000
  error_rate: 0.01
```

---

## Running Tests

### Using Make Commands

```bash
make install         # Install all dependencies
make test            # Run all tests
make eval            # LLM evaluation only
make safety          # AI safety only
make api             # API tests only
make ui              # Playwright UI tests
make load            # Locust load test (10 users, 60s)
make promptfoo       # Run promptfoo evaluation
make lint            # Ruff linter
make all             # Lint + test + load
make clean           # Remove reports/caches
```

### Using Pytest Directly

```bash
# Run by marker
pytest -m llm_eval               # LLM evaluation tests
pytest -m safety                 # AI safety tests
pytest -m api                    # API contract tests
pytest -m ui                     # Playwright UI tests
pytest -m data_validation        # Data validation tests
pytest -m "smoke"                # Quick smoke tests
pytest -m "not slow"             # Skip slow tests

# Run specific test file
pytest evals/test_hallucination_tracking.py -v

# Run with HTML report
pytest --html=reports/report.html --self-contained-html

# Parallel execution
pytest -n auto                   # Auto-detect CPU cores
```

---

## Monitoring

### CloudWatch Dashboard

Import `monitoring/cloudwatch_dashboard.json` into AWS CloudWatch to visualize:
- API request latency (P50/P95/P99)
- Error rates (5xx)
- LLM token usage and costs
- RAG retrieval latency
- Athena query performance

### Latency & Cost Tracker

```bash
python monitoring/latency_cost_tracker.py
```

Outputs real-time snapshot of:
- API latency percentiles
- Hourly LLM token usage and cost
- Error rate with threshold alerts

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-test-suite`)
3. **Write tests** following existing patterns (Page Object for UI, parametrize for data-driven)
4. **Run the full suite** (`make all`)
5. **Submit** a pull request

### Adding New Safety Tests

When a safety test **fails in production**, convert it into a permanent regression test:

1. Add the attack vector to the appropriate data file in `data/safety/`
2. Add a corresponding test case in `safety/`
3. The test should **always be expected to pass** going forward

### Golden Dataset Guidelines

- Each test case needs: `input`, `expected_output`, `retrieval_context`, `ground_truth`
- Cover all medical categories: medication, symptoms, procedures, insurance, general health
- Include at least 2 **refusal behavior** test cases (prescription/diagnosis requests)
- Review and update quarterly with the medical team

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with ❤️ for healthcare AI quality assurance</strong>
</p>
