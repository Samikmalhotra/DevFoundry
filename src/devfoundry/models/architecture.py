from typing import Literal, Optional

from pydantic import BaseModel, Field


class ParameterSpec(BaseModel):
    name: str
    type: str
    required: bool = True
    description: str


class ReturnSpec(BaseModel):
    type: str
    description: str


class FunctionSpec(BaseModel):
    name: str
    description: str
    parameters: list[ParameterSpec] = Field(default_factory=list)
    returns: Optional[ReturnSpec] = None
    raises: list[str] = Field(default_factory=list)


class ClassSpec(BaseModel):
    name: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    methods: list[FunctionSpec] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ModuleSpec(BaseModel):
    name: str
    path: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    classes: list[ClassSpec] = Field(default_factory=list)
    functions: list[FunctionSpec] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class FieldSpec(BaseModel):
    name: str
    type: str
    required: bool = True
    description: str


class DataModelSpec(BaseModel):
    name: str
    description: str
    fields: list[FieldSpec]
    validation_rules: list[str] = Field(default_factory=list)
    examples: list[dict] = Field(default_factory=list)


class InterfaceSpec(BaseModel):
    name: str
    description: str
    methods: list[FunctionSpec] = Field(default_factory=list)


class ApiSpec(BaseModel):
    path: str
    method: Literal[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ]
    description: str
    request_model: Optional[str] = None
    response_model: Optional[str] = None
    authentication_required: bool = False
    error_responses: list[str] = Field(default_factory=list)


class DependencySpec(BaseModel):
    package: str
    version: Optional[str] = None
    purpose: str


class ErrorHandlingSpec(BaseModel):
    strategy: str
    custom_exceptions: list[str] = Field(default_factory=list)
    retry_policy: Optional[str] = None
    logging_strategy: Optional[str] = None


class ValidationSpec(BaseModel):
    input_validation: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    output_validation: list[str] = Field(default_factory=list)


class TestingSpec(BaseModel):
    unit_test_requirements: list[str] = Field(default_factory=list)
    integration_test_requirements: list[str] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    coverage_target: Optional[int] = None


class SecuritySpec(BaseModel):
    authentication: list[str] = Field(default_factory=list)
    authorization: list[str] = Field(default_factory=list)
    input_validation: list[str] = Field(default_factory=list)
    secret_management: list[str] = Field(default_factory=list)
    identified_risks: list[str] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)


class DeploymentSpec(BaseModel):
    runtime: str
    entrypoint: str
    environment_variables: list[str] = Field(default_factory=list)
    deployment_notes: list[str] = Field(default_factory=list)


class ArchitectureSpec(BaseModel):
    project_name: str
    overview: str
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    project_structure: dict
    modules: list[ModuleSpec]
    data_models: list[DataModelSpec]
    interfaces: list[InterfaceSpec]
    api_endpoints: list[ApiSpec]
    dependencies: list[DependencySpec]
    error_handling: ErrorHandlingSpec
    validation_strategy: ValidationSpec
    testing_strategy: TestingSpec
    security_considerations: SecuritySpec
    deployment: DeploymentSpec

    implementation_plan: list[str] = Field(
        default_factory=list
    )

    acceptance_criteria_mapping: dict[
        str,
        list[str]
    ] = Field(
        default_factory=dict
    )