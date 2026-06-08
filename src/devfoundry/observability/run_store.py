import os
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class RunStore:
    def __init__(self, storage_dir: str = "workspace/runs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._active_runs = {}

    def get_run_path(self, run_id: str) -> Path:
        return self.storage_dir / f"{run_id}.json"

    def init_run(self, run_id: str, requirements: str, ui_framework: str) -> dict:
        run_data = {
            "run_id": run_id,
            "project_name": "todo_manager",
            "start_time": datetime.utcnow().isoformat() + "Z",
            "end_time": None,
            "status": "running",
            "requirements": requirements,
            "ui_framework": ui_framework,
            "artifacts": [],
            "events": []
        }
        self._active_runs[run_id] = run_data
        self._save_run(run_data)
        return run_data

    def handle_event(self, event: dict):
        payload = event.get("payload", {})
        run_id = payload.get("run_id")
        if not run_id:
            return

        run_data = self._active_runs.get(run_id)
        if not run_data:
            path = self.get_run_path(run_id)
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        run_data = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading run data for run {run_id}: {e}")

        if not run_data:
            if event["type"] == "crew_started":
                run_data = self.init_run(
                    run_id=run_id,
                    requirements=payload.get("requirements", ""),
                    ui_framework=payload.get("ui_framework", "Gradio")
                )
            else:
                run_data = {
                    "run_id": run_id,
                    "project_name": "todo_manager",
                    "start_time": event["timestamp"],
                    "end_time": None,
                    "status": "running",
                    "requirements": "",
                    "ui_framework": "Gradio",
                    "artifacts": [],
                    "events": []
                }
                self._active_runs[run_id] = run_data

        run_data["events"].append(event)

        if event["type"] == "crew_completed":
            run_data["status"] = "completed"
            run_data["end_time"] = event["timestamp"]
        elif event["type"] == "crew_failed":
            error_msg = payload.get("error", "")
            if "cancelled" in error_msg.lower():
                run_data["status"] = "cancelled"
            else:
                run_data["status"] = "failed"
            run_data["end_time"] = event["timestamp"]
        elif event["type"] == "artifact_written":
            artifact_info = {
                "path": payload.get("path"),
                "size": payload.get("size"),
                "timestamp": event["timestamp"]
            }
            if artifact_info not in run_data["artifacts"]:
                run_data["artifacts"].append(artifact_info)

        self._active_runs[run_id] = run_data
        self._save_run(run_data)

    def _save_run(self, run_data: dict):
        run_id = run_data["run_id"]
        path = self.get_run_path(run_id)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(run_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving run {run_id}: {e}")

    def list_runs(self) -> list:
        runs = []
        if not self.storage_dir.exists():
            return runs
        
        # List json files sorted by modification time (latest first)
        files = list(self.storage_dir.glob("*.json"))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for p in files:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    runs.append({
                        "run_id": data.get("run_id"),
                        "start_time": data.get("start_time"),
                        "end_time": data.get("end_time"),
                        "status": data.get("status"),
                        "requirements": data.get("requirements"),
                        "ui_framework": data.get("ui_framework"),
                        "artifacts_count": len(data.get("artifacts", [])),
                    })
            except Exception as e:
                logger.error(f"Error reading list entry from {p}: {e}")
        return runs

    def get_run(self, run_id: str) -> dict | None:
        path = self.get_run_path(run_id)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading run details for {run_id}: {e}")
        return None


# Global singleton
run_store = RunStore()
