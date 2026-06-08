import os
import yaml
import logging
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from devfoundry.api.schemas import RunRequest
from devfoundry.api.websocket_manager import manager
from devfoundry.observability.event_bus import event_bus
from devfoundry.observability import event_types
from devfoundry.observability.run_store import run_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DevFoundry Observability Server")

# Allow CORS for debugging ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def secure_resolve_path(base_dir: Path, relative_path: str) -> Path:
    """Securely resolves a path to prevent path traversal outside the base directory."""
    resolved = (base_dir / relative_path).resolve()
    if not resolved.is_relative_to(base_dir.resolve()):
        raise HTTPException(status_code=403, detail="Access denied: Path traversal detected")
    return resolved


main_loop = None


def websocket_event_bridge(event: dict):
    """Bridge function that forwards event bus events to connected WebSocket clients."""
    global main_loop
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast(event), main_loop)
    else:
        logger.warning("Main event loop is not running. WebSocket event broadcast skipped.")


# Application Lifespan Events
@app.on_event("startup")
def startup_event():
    global main_loop
    try:
        main_loop = asyncio.get_running_loop()
    except RuntimeError:
        main_loop = asyncio.get_event_loop()

    # 1. Apply CrewAI execution patches
    from devfoundry.observability.patching import apply_patches
    apply_patches()

    # 2. Subscribe bridges and run store to EventBus
    event_bus.subscribe(websocket_event_bridge)
    event_bus.subscribe(run_store.handle_event)
    logger.info("Startup complete: Patches and EventBus listeners initialized.")


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; discard any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# REST Endpoints

def run_crew_thread(requirements: str, ui_framework: str, run_id: str):
    """Background thread target to execute the crew kickoff synchronously."""
    try:
        from devfoundry.workspace.manager import Workspace
        from devfoundry.workspace.context import initialize_workspace
        from devfoundry.crew import DevFoundry

        # Set run_id on event_bus
        event_bus.set_run_id(run_id)

        # Publish starting event
        event_bus.publish(event_types.CREW_STARTED, {
            "requirements": requirements,
            "ui_framework": ui_framework,
            "run_id": run_id
        })

        # Create workspace and global context
        workspace = Workspace(project_name="todo_manager", run_id=run_id)
        initialize_workspace(workspace)

        inputs = {
            "project_name": "todo_manager",
            "run_id": run_id,
            "requirements": requirements,
            "module_name": "todo_manager.py",
            "class_name": "TodoManager",
            "ui_framework": ui_framework
        }

        # Run Crew
        result = DevFoundry(workspace=workspace).crew().kickoff(inputs=inputs)

        # Persist final report
        workspace.write("reports/final_output.md", str(result))

        # Publish completed event
        event_bus.publish(event_types.CREW_COMPLETED, {
            "result": str(result),
            "run_id": run_id
        })
    except Exception as e:
        logger.exception("Error running crew execution")
        # Check if the run has already been finalized/cancelled by the API to avoid duplicate events
        run_info = run_store.get_run(run_id)
        if run_info and run_info.get("status") in ["completed", "failed", "cancelled"]:
            logger.info(f"Run {run_id} was already finalized with status '{run_info.get('status')}'. Skipping duplicate crew failure event.")
            return

        event_bus.publish(event_types.CREW_FAILED, {
            "error": str(e),
            "run_id": run_id
        })


@app.post("/run")
async def start_run(req: RunRequest):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Spawn background thread to run CrewAI workflow non-blockingly
    thread = threading.Thread(
        target=run_crew_thread,
        args=(req.requirements, req.ui_framework, run_id),
        daemon=True
    )
    thread.start()
    
    return {"status": "started", "run_id": run_id}


@app.get("/workflow")
def get_workflow():
    base_path = Path(__file__).parent.parent
    agents_file = base_path / "config" / "agents.yaml"
    tasks_file = base_path / "config" / "tasks.yaml"

    if not agents_file.exists() or not tasks_file.exists():
        raise HTTPException(status_code=500, detail="Configuration files missing")

    try:
        with open(agents_file, "r", encoding="utf-8") as f:
            agents_cfg = yaml.safe_load(f)
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks_cfg = yaml.safe_load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load yaml configs: {e}")

    nodes = []
    edges = []

    # Map tasks to ordering, human roles and tags matching the UI dashboard
    task_order = [
        "analyze_requirements",
        "design_architecture",
        "review_architecture",
        "implement_backend",
        "review_code",
        "create_tests",
        "validate_build",
        "fix_implementation",
        "security_review",
        "generate_ui",
        "generate_documentation",
        "package_project"
    ]

    step_metadata = {
        "analyze_requirements": {
            "step": 1, "tag": "req", "tools": ["WriteFileTool", "ReadFileTool"],
            "artifacts": ["artifacts/requirements.json"]
        },
        "design_architecture": {
            "step": 2, "tag": "arch", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["artifacts/architecture.json"]
        },
        "review_architecture": {
            "step": 3, "tag": "arch", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["artifacts/architecture_review.json"]
        },
        "implement_backend": {
            "step": 4, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool", "CodeExecutor"],
            "artifacts": ["src/main.py", "src/models.py", "src/routes.py", "src/config.py", "requirements.txt"]
        },
        "review_code": {
            "step": 5, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["artifacts/code_review.json"]
        },
        "create_tests": {
            "step": 6, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool", "CodeExecutor"],
            "artifacts": ["tests/test_unit.py", "tests/test_integration.py", "tests/test_edge_cases.py"]
        },
        "validate_build": {
            "step": 7, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool", "CodeExecutor"],
            "artifacts": ["artifacts/validation_report.json"]
        },
        "fix_implementation": {
            "step": 8, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool", "CodeExecutor"],
            "artifacts": []
        },
        "security_review": {
            "step": 9, "tag": "sec", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["artifacts/security_review.json"]
        },
        "generate_ui": {
            "step": 10, "tag": "eng", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["ui/app.py", "ui/components.py"]
        },
        "generate_documentation": {
            "step": 11, "tag": "req", "tools": ["ReadFileTool", "WriteFileTool"],
            "artifacts": ["README.md", "docs/architecture.md", "docs/api.md", "docs/security.md"]
        },
        "package_project": {
            "step": 12, "tag": "mgr", "tools": ["ReadFileTool", "WriteFileTool", "ListFilesTool"],
            "artifacts": ["release/bundle.zip", "release/Dockerfile", "release/docker-compose.yml"]
        }
    }

    role_descriptions = {
        "requirements_analyst": "Senior Product Analyst",
        "architecture_lead": "Principal Software Architect",
        "architecture_reviewer": "Distinguished Architect",
        "backend_engineer": "Senior Software Engineer",
        "code_reviewer": "Senior Code Reviewer",
        "test_engineer": "QA Automation Engineer",
        "execution_engineer": "Validation Engineer",
        "security_engineer": "Application Security Engineer",
        "ui_engineer": "Frontend Engineer",
        "technical_writer": "Technical Documentation Engineer",
        "packaging_engineer": "Release Engineer"
    }

    agent_names = {
        "engineering_manager": "Engineering Manager",
        "requirements_analyst": "Requirements Analyst",
        "architecture_lead": "Architecture Lead",
        "architecture_reviewer": "Architecture Reviewer",
        "backend_engineer": "Backend Engineer",
        "code_reviewer": "Code Reviewer",
        "test_engineer": "Test Engineer",
        "execution_engineer": "Execution Engineer",
        "security_engineer": "Security Engineer",
        "ui_engineer": "UI Engineer",
        "technical_writer": "Technical Writer",
        "packaging_engineer": "Packaging Engineer"
    }

    for t_id in task_order:
        if t_id not in tasks_cfg:
            continue
        t_data = tasks_cfg[t_id]
        agent_key = t_data.get("agent")
        meta = step_metadata.get(t_id, {"step": 99, "tag": "eng", "tools": [], "artifacts": []})

        agent_name = agent_names.get(agent_key, agent_key.replace("_", " ").title() if agent_key else "Agent")
        agent_role = role_descriptions.get(agent_key, agents_cfg.get(agent_key, {}).get("role", "").split("\n")[0].strip())

        nodes.append({
            "id": t_id,
            "step": meta["step"],
            "agent": agent_name,
            "role": agent_role,
            "task": t_data.get("description", "").split("\n")[0][:80],
            "tag": meta["tag"],
            "tools": meta["tools"],
            "artifacts": meta["artifacts"],
            "description": t_data.get("description", "").strip()
        })

        contexts = t_data.get("context", [])
        if isinstance(contexts, str):
            contexts = [contexts]
        for ctx in contexts:
            edges.append({"from": ctx, "to": t_id})

    return {"nodes": nodes, "edges": edges}


@app.get("/artifacts")
def get_artifacts(run_id: str | None = None):
    if not run_id:
        runs = run_store.list_runs()
        if not runs:
            return []
        run_id = runs[0]["run_id"]

    run_info = run_store.get_run(run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail="Run not found")

    project_name = run_info.get("project_name", "todo_manager")
    workspace_dir = Path("workspace") / project_name / run_id

    if not workspace_dir.exists():
        return []

    artifacts = []
    for p in workspace_dir.rglob("*"):
        if p.is_file():
            rel_path = p.relative_to(workspace_dir)
            artifacts.append({
                "path": str(rel_path),
                "size": p.stat().st_size
            })
    return artifacts


@app.get("/artifact/{path:path}")
def get_artifact(path: str, run_id: str | None = None):
    if not run_id:
        runs = run_store.list_runs()
        if not runs:
            raise HTTPException(status_code=404, detail="No runs found")
        run_id = runs[0]["run_id"]

    run_info = run_store.get_run(run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail="Run not found")

    project_name = run_info.get("project_name", "todo_manager")
    workspace_dir = Path("workspace") / project_name / run_id

    # Resolve and validate path securely to prevent traversal attacks
    resolved_path = secure_resolve_path(workspace_dir, path)

    if not resolved_path.exists() or not resolved_path.is_file():
        raise HTTPException(status_code=404, detail=f"Artifact {path} not found")

    try:
        content = resolved_path.read_text(encoding="utf-8")
        return {"path": path, "content": content}
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Cannot read binary file as text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file content: {e}")


@app.get("/runs")
def list_runs():
    return run_store.list_runs()


@app.get("/runs/{run_id}")
def get_run_details(run_id: str):
    run_data = run_store.get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found")
    return run_data


@app.post("/runs/{run_id}/kill")
def kill_run(run_id: str):
    run_info = run_store.get_run(run_id)
    if not run_info:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if run_info.get("status") != "running":
        return {"status": "ignored", "message": f"Run is already in state: {run_info.get('status')}"}

    # Mark the run as cancelled on the event bus
    event_bus.cancel_run(run_id)

    # Immediately publish CREW_FAILED with a cancellation message
    # to update the database status to 'cancelled' and push WebSocket alert
    event_bus.publish(event_types.CREW_FAILED, {
        "error": "Run cancelled by user",
        "run_id": run_id
    })

    return {"status": "cancelled", "run_id": run_id}


# Serves static index dashboard
@app.get("/", response_class=HTMLResponse)
def index():
    index_path = Path("client/devfoundry_monitor.html")
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "Mission Control monitor HTML not found at client/devfoundry_monitor.html"


# Mount static assets files directories
# Create the frontend directory dynamically if it does not exist
Path("frontend").mkdir(parents=True, exist_ok=True)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/client", StaticFiles(directory="client"), name="client")
