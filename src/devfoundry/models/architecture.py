from pydantic import BaseModel

class ArchitectureSpec(BaseModel):
    modules: list[str]
    classes: list[str]
    dependencies: list[str]
    api_design: str