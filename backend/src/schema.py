from pydantic import BaseModel



class SubmittedExam(BaseModel):
    answers: list