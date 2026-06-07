from typing import List, Literal

from pydantic import Field

from devfoundry.models.base import StrictBaseModel


class SecurityFinding(StrictBaseModel):
    title: str

    severity: Literal[
        "critical",
        "high",
        "medium",
        "low",
        "informational",
    ]

    category: Literal[
        "authentication",
        "authorization",
        "input_validation",
        "secrets_management",
        "dependency_risk",
        "cryptography",
        "api_security",
        "session_management",
        "logging",
        "infrastructure",
        "configuration",
        "other",
    ]

    description: str

    affected_component: str

    impact: str

    remediation: str


class SecurityAssessment(StrictBaseModel):
    authentication_reviewed: bool
    authorization_reviewed: bool
    input_validation_reviewed: bool
    secrets_reviewed: bool
    dependency_reviewed: bool
    api_security_reviewed: bool


class SecurityScore(StrictBaseModel):
    score: int = Field(
        ge=0,
        le=100,
        description="Overall security score",
    )

    rating: Literal[
        "excellent",
        "good",
        "fair",
        "poor",
        "critical",
    ]


class SecurityReviewReport(StrictBaseModel):
    overall_risk: Literal[
        "critical",
        "high",
        "medium",
        "low",
    ]

    assessment: SecurityAssessment

    score: SecurityScore

    findings: List[SecurityFinding] = Field(default_factory=list)

    strengths: List[str] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)

    release_blockers: List[str] = Field(default_factory=list)

    approved_for_release: bool