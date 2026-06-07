from typing import Literal

from pydantic import Field

from devfoundry.models.base import StrictBaseModel


class ParameterSpec(StrictBaseModel):
    name: str
    type: str
    required: bool = True
    description: str


class ReturnSpec(StrictBaseModel):
    type: str
    description: str


class FunctionSpec(StrictBaseModel):
    name: str
    description: str
    parameters: list[ParameterSpec] = Field(default_factory=list)
    returns: ReturnSpec | None = None
    raises: list[str] = Field(default_factory=list)


class ClassSpec(StrictBaseModel):
    name: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    methods: list[FunctionSpec] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ModuleSpec(StrictBaseModel):
    name: str
    path: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)
    functions: list[FunctionSpec] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class FieldSpec(StrictBaseModel):
    name: str
    type: str
    required: bool = True
    description: str


class ExampleSpec(StrictBaseModel):
    description: str
    example_json: str


class DataModelSpec(StrictBaseModel):
    name: str
    description: str
    fields: list[FieldSpec] = Field(default_factory=list)
    validation_rules: list[str] = Field(default_factory=list)
    examples: list[ExampleSpec] = Field(default_factory=list)


class InterfaceSpec(StrictBaseModel):
    name: str
    description: str
    methods: list[FunctionSpec] = Field(default_factory=list)


class ApiSpec(StrictBaseModel):
    path: str
    method: Literal[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ]
    description: str
    request_model: str | None = None
    response_model: str | None = None
    authentication_required: bool = False
    error_responses: list[str] = Field(default_factory=list)


class DependencySpec(StrictBaseModel):
    package: str
    version: str | None = None
    purpose: str


class ErrorHandlingSpec(StrictBaseModel):
    strategy: str
    custom_exceptions: list[str] = Field(default_factory=list)
    retry_policy: str | None = None
    logging_strategy: str | None = None


class ValidationSpec(StrictBaseModel):
    input_validation: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    output_validation: list[str] = Field(default_factory=list)


class TestingSpec(StrictBaseModel):
    unit_test_requirements: list[str] = Field(default_factory=list)
    integration_test_requirements: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    coverage_target: int | None = None


class SecuritySpec(StrictBaseModel):
    authentication: list[str] = Field(default_factory=list)
    authorization: list[str] = Field(default_factory=list)
    input_validation: list[str] = Field(default_factory=list)
    secret_management: list[str] = Field(default_factory=list)
    identified_risks: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)


class DeploymentSpec(StrictBaseModel):
    runtime: str
    entrypoint: str
    environment_variables: list[str] = Field(default_factory=list)
    deployment_notes: list[str] = Field(default_factory=list)


class ArchitectureSpec(StrictBaseModel):
    project_name: str
    overview: str

    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    # simple text representation
    project_structure: list[str] = Field(default_factory=list)

    modules: list[ModuleSpec] = Field(default_factory=list)
    data_models: list[DataModelSpec] = Field(default_factory=list)
    interfaces: list[InterfaceSpec] = Field(default_factory=list)
    api_endpoints: list[ApiSpec] = Field(default_factory=list)
    dependencies: list[DependencySpec] = Field(default_factory=list)

    error_handling: ErrorHandlingSpec
    validation_strategy: ValidationSpec
    testing_strategy: TestingSpec
    security_considerations: SecuritySpec
    deployment: DeploymentSpec

    implementation_plan: list[str] = Field(default_factory=list)

    # simple text mappings instead of nested dicts
    acceptance_criteria_mapping: list[str] = Field(default_factory=list)