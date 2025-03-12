from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Question, Option, UserQuestionProgress
)

router = APIRouter()

@router.get("")
def get_review_questions(db: Session = Depends(get_db)):
    """
    GET /review
    Return a list of questions the user last answered incorrectly.
    """
    user_id = 1  # Hardcoded example

    failed_questions = db.query(UserQuestionProgress).filter_by(
        user_id=user_id, last_answer_correct=False
    ).all()

    data = []
    for fq in failed_questions:
        question = db.query(Question).filter(Question.id == fq.question_id).first()
        if question:
            data.append({
                "question_id": question.id,
                "text": question.text,
                "options": [
                    {"option_id": opt.id, "text": opt.text}
                    for opt in question.options
                ]
            })

    return {"failed_questions": data}

@router.post("")
def post_review_answer(payload: dict, db: Session = Depends(get_db)):
    """
    POST /review
    Expects JSON: { "question_id": X, "selected_option_id": Y }
    Attempt to correct a previously failed question.
    """
    user_id = 1
    question_id = payload.get("question_id")
    selected_option_id = payload.get("selected_option_id")

    chosen_option = db.query(Option).filter(Option.id == selected_option_id).first()
    if not chosen_option:
        return {"message": "Option not found or invalid."}, 400

    uq = db.query(UserQuestionProgress).filter_by(
        user_id=user_id, question_id=question_id
    ).first()
    if not uq:
        # If there's no record, create it
        uq = UserQuestionProgress(user_id=user_id, question_id=question_id)
        db.add(uq)

    if chosen_option.is_correct:
        uq.last_answer_correct = True
        uq.times_correct += 1
    else:
        uq.last_answer_correct = False
        uq.times_incorrect += 1

    db.commit()

    return {
        "question_id": question_id,
        "correct": chosen_option.is_correct
    }
