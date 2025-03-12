from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Content, UserContentProgress, UserQuestionProgress
)

router = APIRouter()

@router.get("/next")
def get_next_content(db: Session = Depends(get_db)):
    """
    GET /content/next
    - Illustrates the logic for the work queue: 
      recall -> review -> test -> new content.
    - Currently a placeholder with minimal logic.
    """
    user_id = 1  # Hardcoded example

    # TODO: 
    #   1) Check if user has questions due for recall 
    #   2) Check if user has pending reviews 
    #   3) If user has unpassed content, direct them to exam 
    #   4) Otherwise, serve new content

    return {
        "message": "Next content logic goes here (recall, review, test, or new)."
    }

@router.get("/{content_id}")
def get_content(content_id: int, db: Session = Depends(get_db)):
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
