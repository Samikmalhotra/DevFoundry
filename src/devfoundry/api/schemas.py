from pydantic import BaseModel


class RunRequest(BaseModel):
    requirements: str
    ui_framework: str = "Gradio"
