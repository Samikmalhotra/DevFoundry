from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from devfoundry.models.architecture import ArchitectureSpec
from devfoundry.models.requirements import RequirementsSpec
from devfoundry.models.review import ReviewReport
from devfoundry.models.validation import ValidationReport
from devfoundry.models.security import SecurityReviewReport

from devfoundry.tools.list_files import ListFilesTool
from devfoundry.tools.write_file import WriteFileTool
from devfoundry.tools.read_file import ReadFileTool


@CrewBase
class DevFoundry:
    """DevFoundry"""

    def __init__(self, workspace):
        self.workspace = workspace

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ============================================================
    # Tool Helpers
    # ============================================================

    def rw_tools(self):
        return [
            ReadFileTool(workspace=self.workspace),
            WriteFileTool(workspace=self.workspace),
            ListFilesTool(workspace=self.workspace)
        ]

    # ============================================================
    # Agents
    # ============================================================

    @agent
    def engineering_manager(self):
        return Agent(
            config=self.agents_config["engineering_manager"],
            verbose=True,
            allow_delegation=True,
        )

    @agent
    def requirements_analyst(self):
        return Agent(
            config=self.agents_config["requirements_analyst"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def architecture_lead(self):
        return Agent(
            config=self.agents_config["architecture_lead"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def architecture_reviewer(self):
        return Agent(
            config=self.agents_config["architecture_reviewer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def backend_engineer(self):
        return Agent(
            config=self.agents_config["backend_engineer"],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
            tools=self.rw_tools(),
        )

    @agent
    def code_reviewer(self):
        return Agent(
            config=self.agents_config["code_reviewer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def test_engineer(self):
        return Agent(
            config=self.agents_config["test_engineer"],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
            tools=self.rw_tools(),
        )

    @agent
    def execution_engineer(self):
        return Agent(
            config=self.agents_config["execution_engineer"],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
            tools=self.rw_tools(),
        )

    @agent
    def security_engineer(self):
        return Agent(
            config=self.agents_config["security_engineer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def ui_engineer(self):
        return Agent(
            config=self.agents_config["ui_engineer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def technical_writer(self):
        return Agent(
            config=self.agents_config["technical_writer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def packaging_engineer(self):
        return Agent(
            config=self.agents_config["packaging_engineer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    # ============================================================
    # Tasks
    # ============================================================

    @task
    def analyze_requirements(self):
        return Task(
            config=self.tasks_config["analyze_requirements"],
            output_pydantic=RequirementsSpec,
        )

    @task
    def design_architecture(self):
        return Task(
            config=self.tasks_config["design_architecture"],
            output_pydantic=ArchitectureSpec,
        )

    @task
    def review_architecture(self):
        return Task(
            config=self.tasks_config["review_architecture"],
            output_pydantic=ReviewReport,
        )

    @task
    def implement_backend(self):
        return Task(
            config=self.tasks_config["implement_backend"],
        )

    @task
    def review_code(self):
        return Task(
            config=self.tasks_config["review_code"],
            output_pydantic=ReviewReport,
        )

    @task
    def create_tests(self):
        return Task(
            config=self.tasks_config["create_tests"],
        )

    @task
    def validate_build(self):
        return Task(
            config=self.tasks_config["validate_build"],
            output_pydantic=ValidationReport,
        )

    @task
    def fix_implementation(self):
        return Task(
            config=self.tasks_config["fix_implementation"],
        )

    @task
    def security_review(self):
        return Task(
            config=self.tasks_config["security_review"],
            output_pydantic=SecurityReviewReport,
        )

    @task
    def generate_ui(self):
        return Task(
            config=self.tasks_config["generate_ui"],
        )

    @task
    def generate_documentation(self):
        return Task(
            config=self.tasks_config["generate_documentation"],
        )

    @task
    def package_project(self):
        return Task(
            config=self.tasks_config["package_project"],
        )

    @crew
    def crew(self):
        analyze_requirements = self.analyze_requirements()
        analyze_requirements.__dict__["task_id"] = "analyze_requirements"

        design_architecture = self.design_architecture()
        design_architecture.__dict__["task_id"] = "design_architecture"

        review_architecture = self.review_architecture()
        review_architecture.__dict__["task_id"] = "review_architecture"

        implement_backend = self.implement_backend()
        implement_backend.__dict__["task_id"] = "implement_backend"

        review_code = self.review_code()
        review_code.__dict__["task_id"] = "review_code"

        create_tests = self.create_tests()
        create_tests.__dict__["task_id"] = "create_tests"

        validate_build = self.validate_build()
        validate_build.__dict__["task_id"] = "validate_build"

        fix_implementation = self.fix_implementation()
        fix_implementation.__dict__["task_id"] = "fix_implementation"

        security_review = self.security_review()
        security_review.__dict__["task_id"] = "security_review"

        generate_ui = self.generate_ui()
        generate_ui.__dict__["task_id"] = "generate_ui"

        generate_documentation = self.generate_documentation()
        generate_documentation.__dict__["task_id"] = "generate_documentation"

        package_project = self.package_project()
        package_project.__dict__["task_id"] = "package_project"

        return Crew(
            agents=[
                self.requirements_analyst(),
                self.architecture_lead(),
                self.architecture_reviewer(),
                self.backend_engineer(),
                self.code_reviewer(),
                self.test_engineer(),
                self.execution_engineer(),
                self.security_engineer(),
                self.ui_engineer(),
                self.technical_writer(),
                self.packaging_engineer(),
            ],
            tasks=[
                analyze_requirements,
                design_architecture,
                review_architecture,
                implement_backend,
                review_code,
                create_tests,
                validate_build,
                fix_implementation,
                security_review,
                generate_ui,
                generate_documentation,
                package_project,
            ],
            manager_agent=self.engineering_manager(),
            process=Process.hierarchical,
            verbose=True,
            memory=False,
            cache=False,
            planning=False,
        )