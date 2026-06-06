from pydantic import BaseModel

class ReviewReport(BaseModel):
    approved: bool
    findings: list[str]
    recommendations: list[str]