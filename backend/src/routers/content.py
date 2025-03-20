from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Content, UserContentProgress, UserQuestionProgress
)
from recall import get_recall_questions
from review import get_review_questions

router = APIRouter()

@router.get("/next")
def get_next_content(db: Session = Depends(get_db)):
    """
    GET /content/next
    - Illustrates the logic for the work queue: 
      recall -> review -> new content.
    - Currently a placeholder with minimal logic.
    """
    user_id = 1  # Hardcoded example

    #   1) Check if user has questions due for recall
    recall_questions = get_recall_questions()
    if len(recall_questions["due_recall_questions"]) > 0:
        return recall_questions

    #   2) Check if user has pending reviews 
    review_questions = get_review_questions()
    if len(review_questions["failed_questions"]):
        return review_questions
    #   3) Otherwise, serve new content
    last_content = None #placeholder
    return get_content(last_content)


@router.get("/{content_id}")
def get_content(content_id: int = Path(description="ID number of the content to GET from database"), db: Session = Depends(get_db)):
    """
    GET /content/{content_id}
    Return the details of a specific lesson/content unit.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return {
        "id": content.id,
        "title": content.title,
        "body": content.body,
        "level_id": content.level_id
    }

@router.post("/{content_id}/newcontent")
def new_content(content_id: int, db: Session = Depends(get_db)):
    pass