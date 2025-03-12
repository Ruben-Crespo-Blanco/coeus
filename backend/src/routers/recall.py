from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Question, Option, UserQuestionProgress
)

router = APIRouter()

@router.get("")
def get_recall_questions(db: Session = Depends(get_db)):
    """
    GET /remember
    Return a set of previously learned questions due for spaced repetition (next_review_date <= now).
    """
    user_id = 1  # Hardcoded

    now = datetime.utcnow()
    due_questions = db.query(UserQuestionProgress).filter(
        UserQuestionProgress.user_id == user_id,
        UserQuestionProgress.next_review_date != None,
        UserQuestionProgress.next_review_date <= now
    ).all()

    data = []
    for uq in due_questions:
        q = db.query(Question).filter(Question.id == uq.question_id).first()
        if q:
            data.append({
                "question_id": q.id,
                "text": q.text,
                "options": [
                    {"option_id": opt.id, "text": opt.text}
                    for opt in q.options
                ]
            })

    return {"due_recall_questions": data}

@router.post("/submit")
def submit_recall_answers(payload: dict, db: Session = Depends(get_db)):
    """
    POST /remember/submit
    Expects JSON: { "answers": [ { "question_id": X, "option_id": Y }, ... ] }
    """
    user_id = 1  # Hardcoded
    now = datetime.utcnow()

    answers = payload.get("answers", [])
    for ans in answers:
        question_id = ans["question_id"]
        option_id = ans["option_id"]

        chosen_option = db.query(Option).filter(Option.id == option_id).first()
        uq = db.query(UserQuestionProgress).filter_by(
            user_id=user_id, question_id=question_id
        ).first()
        if not uq:
            # Create new progress record if doesn't exist
            uq = UserQuestionProgress(user_id=user_id, question_id=question_id)
            db.add(uq)

        if chosen_option and chosen_option.is_correct:
            uq.last_answer_correct = True
            uq.times_correct += 1
            # Example: Next review in 7 days
            uq.next_review_date = now + timedelta(days=7)
        else:
            uq.last_answer_correct = False
            uq.times_incorrect += 1
            # Fail => schedule sooner
            uq.next_review_date = now + timedelta(days=1)

    db.commit()
    return {"message": "Recall answers processed. Next reviews scheduled."}
