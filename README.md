# DevFoundry

## Overview

DevFoundry is a multi-agent software engineering platform built using CrewAI. It transforms natural language requirements into a complete software project by orchestrating specialized AI agents responsible for requirements analysis, architecture design, implementation, testing, security review, documentation generation, UI creation, and packaging.

The system follows a structured engineering workflow that mimics a real software development organization, where each stage of the software lifecycle is validated and managed with rich real-time observability.

---

# Key Features

* Requirements analysis and specification generation
* Technical architecture design
* Architecture review and validation
* Backend implementation generation
* Automated code review
* Test suite generation
* Build and validation analysis
* Security assessment
* UI generation
* Documentation generation
* Project packaging and release preparation
* Hierarchical agent coordination using CrewAI
* **Real-time Observability Dashboard (Mission Control)** to visualize and manage runs
* **Event-Driven Tracking** of tasks, agents, tools, and custom delegation flows
* **WebSocket Streams** broadcasting agent progress and console logs live
* **REST & WebSockets API Server** for programmatic workflow execution and run control

---

# Architecture

DevFoundry uses a hierarchical CrewAI process.

```text
User Requirements
        │
        ▼
Requirements Analyst
        │
        ▼
Architecture Lead
        │
        ▼
Architecture Reviewer
        │
        ▼
Backend Engineer
        │
        ├─────────────► Code Reviewer
        │
        ├─────────────► Test Engineer
        │                    │
        │                    ▼
        │            Execution Engineer
        │
        ▼
Security Engineer
        │
        ▼
UI Engineer
        │
        ▼
Technical Writer
        │
        ▼
Packaging Engineer
```

All work is coordinated by the Engineering Program Manager operating as the Crew Manager.

---

# Agent Responsibilities

## Engineering Manager

Coordinates all engineering activities and oversees project execution.

Responsibilities:

* Manage workflow progression
* Coordinate agents
* Ensure quality gates are met
* Resolve task dependencies

---

## Requirements Analyst

Transforms user requirements into a structured specification.

Produces:

* Functional requirements
* Non-functional requirements
* Assumptions
* Constraints
* Risks
* Edge cases
* Acceptance criteria
* Open questions

Output:

```text
requirements/requirements.json
```

---

## Architecture Lead

Designs the system architecture based on approved requirements.

Produces:

* Project structure
* Modules
* Classes
* Interfaces
* APIs
* Data models
* Error handling strategy
* Testing strategy
* Security considerations

Output:

```text
architecture/architecture.json
```

---

## Architecture Reviewer

Evaluates the architecture for:

* Scalability
* Security
* Maintainability
* Testability
* Completeness
* Consistency

Output:

```text
reports/architecture_review.json
```

---

## Backend Engineer

Implements the architecture.

Produces:

* Source code
* Project structure
* Configuration
* Dependencies

Uses:

* ReadFileTool
* WriteFileTool

---

## Code Reviewer

Reviews generated code.

Evaluates:

* Correctness
* Design adherence
* Security
* Maintainability
* Performance

Output:

```text
reports/code_review.json
```

---

## Test Engineer

Creates comprehensive test coverage.

Produces:

* Unit tests
* Integration tests
* Error scenario tests
* Edge-case tests

---

## Execution Engineer

Validates generated implementation.

Analyzes:

* Test outputs
* Runtime failures
* Linting results
* Type checking results

Output:

```text
reports/validation_report.json
```

---

## Security Engineer

Performs application security review.

Evaluates:

* Authentication
* Authorization
* Input validation
* Secret management
* Injection vulnerabilities
* Data handling practices

Output:

```text
reports/security_review.json
```

---

## UI Engineer

Generates a demonstration interface.

Supported UI technologies:

* Gradio
* Streamlit
* FastAPI
* React

The UI framework is configurable through workflow inputs.

---

## Technical Writer

Generates project documentation.

Produces:

* README
* Setup instructions
* Architecture overview
* API documentation
* Usage examples

---

## Packaging Engineer

Creates the final deliverable.

Produces:

* Packaging configuration
* Deployment assets
* Final project structure
* Documentation bundle

---

# Workflow

The project executes the following tasks in order:

1. Analyze Requirements
2. Design Architecture
3. Review Architecture
4. Implement Backend
5. Review Code
6. Create Tests
7. Validate Build
8. Fix Implementation
9. Security Review
10. Generate UI
11. Generate Documentation
12. Package Project

---

# Project Structure

```text
DevFoundry/
├── client/
│   └── devfoundry_monitor.html         # Mission Control UI HTML dashboard
├── frontend/
│   ├── api.js                          # REST API Client wrapper
│   └── websocket.js                    # WebSockets connection helper
├── src/
│   └── devfoundry/
│       ├── api/
│       │   ├── schemas.py              # Pydantic schemas for requests
│       │   ├── server.py               # FastAPI application backend
│       │   └── websocket_manager.py    # WebSocket client manager
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── models/
│       │   ├── requirements.py
│       │   ├── architecture.py
│       │   └── review.py
│       ├── observability/
│       │   ├── event_bus.py            # Central thread-safe EventBus singleton
│       │   ├── event_types.py          # Defined event categories
│       │   ├── patching.py             # CrewAI monkey-patching logic
│       │   └── run_store.py            # Persistent storage manager for runs
│       ├── tools/
│       │   ├── read_file.py            # Custom read tool with observability hooks
│       │   └── write_file.py           # Custom write tool with observability hooks
│       ├── workspace/
│       │   ├── manager.py
│       │   └── context.py
│       ├── crew.py                     # Crew definition
│       └── main.py                     # CLI Entry point
├── pyproject.toml
└── uv.lock
```

Generated workspace output:

```text
workspace/
└── <project_name>/
    └── <run_id>/
        ├── requirements/
        ├── architecture/
        ├── reports/
        ├── src/
        ├── tests/
        ├── ui/
        ├── docs/
        └── package/
```

Workspace run records database:

```text
workspace/
└── runs/
    └── <run_id>.json                  # Complete persistent event stream & metadata
```

---

# Configuration

## Agents

Agent definitions are stored in:

```text
config/agents.yaml
```

This file defines:

* Agent roles
* Goals
* Backstories
* Specialization

---

## Tasks

Workflow definitions are stored in:

```text
config/tasks.yaml
```

This file defines:

* Task descriptions
* Context dependencies
* Expected outputs
* Assigned agents

---

# Example Usage

## CLI Execution

```python
from devfoundry.crew import DevFoundry
from devfoundry.workspace.manager import Workspace

workspace = Workspace("todo_manager")

inputs = {
    "project_name": "todo_manager",
    "requirements": """
    Create a todo list management system.
    Users should be able to add, remove,
    complete and list tasks.
    """,
    "module_name": "todo_manager.py",
    "class_name": "TodoManager",
    "ui_framework": "Gradio"
}

result = DevFoundry(
    workspace=workspace
).crew().kickoff(inputs=inputs)
```

## Running the Observability API & Mission Control Dashboard

To start the FastAPI web server hosting the REST endpoints, WebSockets stream, and Mission Control dashboard:

```bash
uv run uvicorn devfoundry.api.server:app --host 0.0.0.0 --port 8000 --reload
```

Once started, open your web browser and navigate to:
```text
http://localhost:8000/
```

---

# Real-time Observability & Mission Control

DevFoundry features a comprehensive **Mission Control Dashboard** and an event-driven **Observability Server** that provides deep, real-time insights into CrewAI multi-agent runs, task completions, agent interactions, and tool calls.

## How It Works

1. **Monkey Patching CrewAI Components**:
   Upon server startup, DevFoundry dynamically hooks into CrewAI's core execution flow:
   - **`Task.execute_sync` / `execute_async`**: Captures when a task starts, completes, fails, or emits special findings (such as security warnings or validation errors).
   - **`Agent.execute_task`**: Traces the active agent execution context.
   - **`DelegateWorkTool` / `AskQuestionTool`**: Intercepts and logs agent-to-agent delegation events (showing who is delegating what to whom).
2. **Central Event Bus**:
   A thread-safe `EventBus` aggregates execution logs, tool reports, and delegation details, broadcasting them instantly to all registered listeners.
3. **Persistent Run Storage**:
   Every execution is assigned a unique `run_id` (e.g., `YYYYMMDD_HHMMSS`). The `RunStore` listens to the event bus and persists the complete run details (events list, run status, start/end timestamps, input parameters, generated artifacts list) to `workspace/runs/<run_id>.json`.
4. **WebSocket Streaming**:
   An event bridge automatically routes published events from the backend `EventBus` to the WebSocket connection `/ws`, updating the frontend in real time.

---

## API Endpoints Reference

The FastAPI server provides several endpoints to manage, query, and trigger agent workflows.

### REST Endpoints
* **`POST /run`**: Kickoff a new project generation run.
  - **Payload**: `{"requirements": "...", "ui_framework": "Gradio"}`
  - **Response**: `{"status": "started", "run_id": "..."}`
* **`GET /workflow`**: Retrieves the statically defined task hierarchy (nodes, dependencies, assigned agents, and descriptions) mapped as a DAG.
* **`GET /runs`**: Lists all recorded runs sorted by timestamp (latest first) showing duration, status, and artifact count.
* **`GET /runs/{run_id}`**: Fetches the complete JSON data and event stream for a specific run.
* **`POST /runs/{run_id}/kill`**: Immediately requests cancellation of an active run. Setting a cancellation flag causes running agents and tools to safely raise a termination exception.
* **`GET /artifacts?run_id={run_id}`**: Lists all files currently generated by a specific run.
* **`GET /artifact/{path}?run_id={run_id}`**: Retrieves the raw text content of a generated artifact file.

### WebSocket Endpoint
* **`WS /ws`**: Establishes a WebSocket connection to receive real-time JSON event payloads.

---

## Mission Control UI Dashboard

The UI dashboard serves as the central control panel. It is served automatically at the root URL (`/`) of the server and connects to the WebSockets API.

### Key Visual Components
* **Control Board**: Form to specify prompt requirements, choose UI framework, and run/cancel executions.
* **Interactive Workflow DAG**: Displays the 12-stage sequential workflow task nodes. Nodes light up dynamically in colors based on status (Pending: gray, Running: blue, Completed: green, Failed: red).
* **Agent Delegation & Co-operation Feed**: Real-time ticker showing agent communication, including who delegated to whom.
* **Event & Tool Execution Log**: Live scrollable terminal displaying agent logs, file reads/writes, tool starts/finishes, and validation/security warnings.
* **Artifact Inspector**: An interactive file explorer displaying generated code files, specifications, and reports. Clicking a file renders its contents directly in the dashboard UI.
* **Runs History Sidebar**: Easily switch between current and past executions to inspect completed files or logs.

---

# Example Generated Application

Input:

```text
Create a todo list management system.
```

Potential outputs:

* Requirements specification
* Architecture design
* Python implementation
* Unit tests
* Gradio UI
* Documentation
* Security review
* Packaged project

---

# Technology Stack

* Python 3.11+
* CrewAI
* FastAPI
* Uvicorn
* Pydantic
* YAML
* Gradio (optional)
* Streamlit (optional)
* React (optional)

---

# Current Limitations

* No automatic remediation loop after reviews
* Architecture review feedback is not automatically incorporated
* Validation does not execute build tools directly
* Review stages currently occur only once
* Quality gates are advisory rather than enforced

---

# Future Enhancements

* Self-healing remediation cycles
* Architecture revision loop
* Automated test execution
* Linting and type-checking integration
* Continuous quality gates
* Multi-language code generation
* Git integration
* Deployment generation
* CI/CD pipeline generation

---

# Vision

DevFoundry aims to function as an autonomous engineering organization capable of transforming requirements into production-ready software through coordinated AI agents while maintaining engineering best practices and software quality standards.
