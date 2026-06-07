from typing import List, Literal
from pydantic import Field

from devfoundry.models.base import StrictBaseModel


class ValidationIssue(StrictBaseModel):
    title: str
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal[
        "build",
        "test",
        "lint",
        "type_check",
        "runtime",
        "dependency",
        "configuration",
        "other",
    ]
    description: str
    root_cause: str
    recommendation: str


class ValidationSummary(StrictBaseModel):
    build_passed: bool
    tests_passed: bool
    lint_passed: bool
    type_check_passed: bool
    runtime_validation_passed: bool


class ValidationMetrics(StrictBaseModel):
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    lint_errors: int = 0
    lint_warnings: int = 0
    type_errors: int = 0


class ValidationReport(StrictBaseModel):
    overall_status: Literal["passed", "failed", "passed_with_warnings"]

    summary: ValidationSummary

    metrics: ValidationMetrics

    issues: List[ValidationIssue] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)

    blocking_issues: List[str] = Field(
        default_factory=list,
        description="Issues that must be resolved before release",
    )

    release_ready: bool