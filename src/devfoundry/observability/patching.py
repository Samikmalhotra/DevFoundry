import json
import logging
import asyncio
from contextvars import ContextVar
from crewai import Agent, Task
from crewai.tools.agent_tools.delegate_work_tool import DelegateWorkTool
from crewai.tools.agent_tools.ask_question_tool import AskQuestionTool

from devfoundry.observability.event_bus import event_bus
from devfoundry.observability import event_types

logger = logging.getLogger(__name__)

# Context variable to track the currently running agent role
current_agent_role: ContextVar[str] = ContextVar("current_agent_role", default="Engineering Manager")


def apply_patches():
    logger.info("Applying observability patches to CrewAI classes...")

    # 1. Patch Task.execute_sync and execute_async
    original_execute_sync = Task.execute_sync
    original_execute_async = Task.execute_async

    def new_execute_sync(self, agent=None, context=None, tools=None):
        if event_bus.is_run_cancelled():
            raise RuntimeError("Run cancelled by user")

        task_id = getattr(self, "task_id", None) or self.name or self.description
        if not task_id:
            task_id = self.description.split("\n")[0][:60]

        assigned_agent = agent or self.agent
        agent_role = getattr(assigned_agent, "role", "Unknown Agent")

        event_bus.publish(event_types.TASK_STARTED, {
            "task": task_id,
            "agent": agent_role,
            "description": self.description
        })

        try:
            if event_bus.is_run_cancelled():
                raise RuntimeError("Run cancelled by user")
            res = original_execute_sync(self, agent, context, tools)
            if event_bus.is_run_cancelled():
                raise RuntimeError("Run cancelled by user")
            
            # Post-task output checks (validation failures, security findings)
            check_and_emit_special_findings(task_id, res)

            event_bus.publish(event_types.TASK_COMPLETED, {
                "task": task_id,
                "agent": agent_role,
                "output": str(res)
            })
            return res
        except Exception as e:
            event_bus.publish(event_types.TASK_FAILED, {
                "task": task_id,
                "agent": agent_role,
                "error": str(e)
            })
            raise e

    async def new_execute_async(self, agent=None, context=None, tools=None):
        if event_bus.is_run_cancelled():
            raise RuntimeError("Run cancelled by user")

        task_id = getattr(self, "task_id", None) or self.name or self.description
        if not task_id:
            task_id = self.description.split("\n")[0][:60]

        assigned_agent = agent or self.agent
        agent_role = getattr(assigned_agent, "role", "Unknown Agent")

        event_bus.publish(event_types.TASK_STARTED, {
            "task": task_id,
            "agent": agent_role,
            "description": self.description
        })

        try:
            if event_bus.is_run_cancelled():
                raise RuntimeError("Run cancelled by user")
            res = await original_execute_async(self, agent, context, tools)
            if event_bus.is_run_cancelled():
                raise RuntimeError("Run cancelled by user")
            
            check_and_emit_special_findings(task_id, res)

            event_bus.publish(event_types.TASK_COMPLETED, {
                "task": task_id,
                "agent": agent_role,
                "output": str(res)
            })
            return res
        except Exception as e:
            event_bus.publish(event_types.TASK_FAILED, {
                "task": task_id,
                "agent": agent_role,
                "error": str(e)
            })
            raise e

    Task.execute_sync = new_execute_sync
    Task.execute_async = new_execute_async

    # 2. Patch Agent.execute_task to set current_agent_role and emit agent started/completed events
    original_execute_task = Agent.execute_task

    def new_execute_task(self, task, context=None, tools=None):
        if event_bus.is_run_cancelled():
            raise RuntimeError("Run cancelled by user")
        role = self.role
        token = current_agent_role.set(role)

        event_bus.publish(event_types.AGENT_STARTED, {
            "agent": role,
            "task": task.description
        })

        try:
            res = original_execute_task(self, task, context, tools)
            event_bus.publish(event_types.AGENT_COMPLETED, {
                "agent": role,
                "task": task.description
            })
            return res
        finally:
            current_agent_role.reset(token)

    Agent.execute_task = new_execute_task

    # 3. Patch delegation tools (_execute method)
    def patch_delegation_tool(tool_class):
        original_exec = tool_class._execute

        def new_exec(self, agent_name: str | None, task: str, context: str | None = None):
            if event_bus.is_run_cancelled():
                raise RuntimeError("Run cancelled by user")
            to_agent = agent_name or "Unknown Agent"
            from_agent = current_agent_role.get("Engineering Manager")

            event_bus.publish(event_types.DELEGATION, {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "task": task
            })
            return original_exec(self, agent_name, task, context)

        tool_class._execute = new_exec

    patch_delegation_tool(DelegateWorkTool)
    patch_delegation_tool(AskQuestionTool)
    logger.info("Observability patches applied successfully.")


def check_and_emit_special_findings(task_id: str, task_output):
    """Parses task output to check for validation status and security findings."""
    try:
        from devfoundry.models.validation import ValidationReport
        from devfoundry.models.security import SecurityReviewReport

        raw_output = getattr(task_output, "raw", str(task_output))
        pyd_output = getattr(task_output, "pydantic", None)

        if "validate_build" in task_id.lower():
            report = None
            if isinstance(pyd_output, ValidationReport):
                report = pyd_output
            elif isinstance(pyd_output, dict):
                report = ValidationReport.model_validate(pyd_output)
            else:
                try:
                    data = json.loads(raw_output)
                    report = ValidationReport.model_validate(data)
                except Exception:
                    pass

            if report:
                if report.overall_status == "failed" or not report.release_ready or report.issues:
                    errors = [f"{issue.title}: {issue.description}" for issue in report.issues]
                    event_bus.publish(event_types.VALIDATION_FAILED, {
                        "task": task_id,
                        "errors": errors or ["Build validation failed"]
                    })

        elif "security_review" in task_id.lower():
            report = None
            if isinstance(pyd_output, SecurityReviewReport):
                report = pyd_output
            elif isinstance(pyd_output, dict):
                report = SecurityReviewReport.model_validate(pyd_output)
            else:
                try:
                    data = json.loads(raw_output)
                    report = SecurityReviewReport.model_validate(data)
                except Exception:
                    pass

            if report and report.findings:
                findings = [f"{f.title} (Severity: {f.severity})" for f in report.findings]
                event_bus.publish(event_types.SECURITY_FINDING, {
                    "task": task_id,
                    "findings": findings
                })
    except Exception as e:
        logger.error(f"Error parsing task outputs for special findings: {e}")
