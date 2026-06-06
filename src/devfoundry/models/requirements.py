from pydantic import BaseModel

class RequirementsSpec(BaseModel):
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    assumptions: list[str]
    risks: list[str]
    acceptance_criteria: list[str]