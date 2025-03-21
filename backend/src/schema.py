from pydantic import BaseModel, StringConstraints
from sqlalchemy import Integer, String
from typing import Annotated


class SubmittedExam(BaseModel):
    answers: list

class NewContent(BaseModel):
    title: Annotated[str, StringConstraints(max_length=100)]
    body: str|None = None
    course_id: int