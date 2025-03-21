from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
from src.database import get_db
from src.models import (
    Content, UserContentProgress, UserQuestionProgress
)
from schema import NewContent
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
    
    progress = db.query(UserContentProgress).filter(Content.id == content_id).first()
    if progress.available:
        return {
            "id": content.id,
            "title": content.title,
            "body": content.body,
            "level_id": content.level_id
        }
    else: 
        raise HTTPException(status_code=403, detail="Content not available to you yet")

@router.post("/{content_id}/newcontent")
def new_content(new_content: NewContent, db: Session = Depends(get_db)):
    

    try:
        # Find the max order_index for this course (or level)
        max_index = db.query(func.max(Content.order_index)).filter(Content.level_id == new_content.course_id).scalar()

        next_order_index = (max_index or 0) + 1  # Start at 1 if none exists

        # Create a new Content object
        db_content = Content(
            title=new_content.title,
            body=new_content.body,
            course_id=new_content.course_id,
            order_index=next_order_index,
        )

        db.add(db_content)
        db.commit()
        db.refresh(db_content)

        return {
            "id": db_content.id,
            "title": db_content.title,
            "message": "New content created successfully"
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error: possible duplicate or constraint violation")

    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error")
