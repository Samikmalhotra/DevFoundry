from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from devfoundry.models.architecture import ArchitectureSpec
from devfoundry.models.requirements import RequirementsSpec
from devfoundry.models.review import ReviewReport

from devfoundry.tools.write_file import WriteFileTool
from devfoundry.tools.read_file import ReadFileTool


@CrewBase
class DevFoundry:
    """DevFoundry v2"""

    def __init__(self, workspace):
        self.workspace = workspace

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ============================================================
    # Tool Helpers
    # ============================================================

    def read_tools(self):
        return [
            ReadFileTool(workspace=self.workspace),
        ]

    def rw_tools(self):
        return [
            ReadFileTool(workspace=self.workspace),
            WriteFileTool(workspace=self.workspace),
        ]

    # ============================================================
    # Agents
    # ============================================================

    @agent
    def engineering_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["engineering_manager"],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def requirements_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["requirements_analyst"],
            verbose=True,
        )

    @agent
    def architecture_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["architecture_lead"],
            verbose=True,
            tools = self.rw_tools()
        )

    @agent
    def architecture_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["architecture_reviewer"],
            verbose=True,
            tools=self.read_tools(),
        )

    @agent
    def backend_engineer(self) -> Agent:
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
    def code_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["code_reviewer"],
            verbose=True,
            tools=self.read_tools(),
        )

    @agent
    def test_engineer(self) -> Agent:
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
    def execution_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["execution_engineer"],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
            tools=self.read_tools(),
        )

    @agent
    def security_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["security_engineer"],
            verbose=True,
            tools=self.read_tools(),
        )

    @agent
    def ui_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_engineer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def technical_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_writer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    @agent
    def packaging_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["packaging_engineer"],
            verbose=True,
            tools=self.rw_tools(),
        )

    # ============================================================
    # Tasks
    # ============================================================

    @task
    def analyze_requirements(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_requirements"],
            output_pydantic=RequirementsSpec,
            output_file="requirements/requirements.json",
        )

    @task
    def design_architecture(self) -> Task:
        return Task(
            config=self.tasks_config["design_architecture"],
            output_pydantic=ArchitectureSpec,
            output_file="architecture/architecture.json",
        )

    @task
    def review_architecture(self) -> Task:
        return Task(
            config=self.tasks_config["review_architecture"],
            output_pydantic=ReviewReport,
            output_file="reports/architecture_review.json",
        )

    @task
    def implement_backend(self) -> Task:
        return Task(
            config=self.tasks_config["implement_backend"],
        )

    @task
    def review_code(self) -> Task:
        return Task(
            config=self.tasks_config["review_code"],
            output_pydantic=ReviewReport,
            output_file="reports/code_review.json",
        )

    @task
    def create_tests(self) -> Task:
        return Task(
            config=self.tasks_config["create_tests"],
        )

    @task
    def validate_build(self) -> Task:
        return Task(
            config=self.tasks_config["validate_build"],
            output_file="reports/validation_report.json",
        )

    @task
    def fix_implementation(self) -> Task:
        return Task(
            config=self.tasks_config["fix_implementation"],
        )

    @task
    def security_review(self) -> Task:
        return Task(
            config=self.tasks_config["security_review"],
            output_file="reports/security_review.json",
        )

    @task
    def generate_ui(self) -> Task:
        return Task(
            config=self.tasks_config["generate_ui"],
        )

    @task
    def generate_documentation(self) -> Task:
        return Task(
            config=self.tasks_config["generate_documentation"],
        )

    @task
    def package_project(self) -> Task:
        return Task(
            config=self.tasks_config["package_project"],
        )

    # ============================================================
    # Crew
    # ============================================================

    @crew
    def crew(self) -> Crew:
        """Creates the DevFoundry v2 crew"""

        requirements = self.analyze_requirements()
        architecture = self.design_architecture()
        architecture_review = self.review_architecture()
        implementation = self.implement_backend()
        code_review = self.review_code()
        tests = self.create_tests()
        validation = self.validate_build()
        fixes = self.fix_implementation()
        security = self.security_review()
        ui = self.generate_ui()
        docs = self.generate_documentation()
        package = self.package_project()

        tasks = [
            requirements,
            architecture,
            architecture_review,
            implementation,
            code_review,
            tests,
            validation,
            fixes,
            security,
            ui,
            docs,
            package,
        ]

        agents = [
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
        ]

        return Crew(
            agents=agents,
            tasks=tasks,
            manager_agent=self.engineering_manager(),
            process=Process.hierarchical,
            verbose=True,
            memory=False,
            cache=True,
            planning=True,
        )
