import threading
import logging
from datetime import datetime
from contextvars import ContextVar
from typing import Callable, List

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._listeners: List[Callable[[dict], None]] = []
        self._lock = threading.Lock()
        self.active_run_id = ContextVar("active_run_id", default="")
        self._global_run_id = ""
        self._cancelled_runs = set()
        self._cancellation_lock = threading.Lock()

    def cancel_run(self, run_id: str):
        with self._cancellation_lock:
            self._cancelled_runs.add(run_id)
            logger.info(f"Run {run_id} marked as cancelled.")

    def is_run_cancelled(self, run_id: str | None = None) -> bool:
        if not run_id:
            run_id = self.get_run_id()
        if not run_id:
            return False
        with self._cancellation_lock:
            return run_id in self._cancelled_runs

    def subscribe(self, listener: Callable[[dict], None]):
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)
                logger.info(f"Subscribed new listener. Total: {len(self._listeners)}")

    def unsubscribe(self, listener: Callable[[dict], None]):
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)
                logger.info(f"Unsubscribed listener. Total: {len(self._listeners)}")

    def set_run_id(self, run_id: str):
        self.active_run_id.set(run_id)
        self._global_run_id = run_id
        logger.info(f"EventBus run_id set to: {run_id}")

    def get_run_id(self) -> str:
        rid = self.active_run_id.get()
        if not rid:
            rid = self._global_run_id
        return rid

    def publish(self, event_type: str, payload: dict):
        run_id = payload.get("run_id") or self.get_run_id()
        if "run_id" not in payload and run_id:
            payload["run_id"] = run_id

        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": payload
        }

        with self._lock:
            listeners = list(self._listeners)

        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error invoking listener in EventBus: {e}", exc_info=True)


# Global singleton
event_bus = EventBus()
