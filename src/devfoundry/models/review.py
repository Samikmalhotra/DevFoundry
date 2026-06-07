from typing import Literal

from pydantic import BaseModel

class Finding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: str
    description: str
    impact: str
    recommendation: str

class ReviewReport(BaseModel):
    approved: bool
    summary: str
    findings: list[Finding]
    recommendations: list[str]
    risks: list[str]