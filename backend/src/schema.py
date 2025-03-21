from pydantic import BaseModel, StringConstraints
from sqlalchemy import Integer, String
from typing import Annotated


class SubmittedExam(BaseModel):
    answers: list

class NewContent(BaseModel):
    title: Annotated[str, StringConstraints(max_length=100)]
    body: str|None = None
    course_id: int

class ContentUpdate(BaseModel):
    id: int
    title: Annotated[str|None, StringConstraints(max_length=100)] = None
    body: str | None = None
    course_id: int | None = None
    order_index: int|None = None