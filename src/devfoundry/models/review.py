from typing import Literal

from devfoundry.models.base import StrictBaseModel

class Finding(StrictBaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: str
    description: str
    impact: str
    recommendation: str

class ReviewReport(StrictBaseModel):
    approved: bool
    summary: str
    findings: list[Finding]
    recommendations: list[str]
    risks: list[str]