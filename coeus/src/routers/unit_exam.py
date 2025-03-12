import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Level, Question, Option, UserQuestionProgress
)

router = APIRouter()

@router.get("/{level_id}")
def start_unit_exam(level_id: int, db: Session = Depends(get_db)):
    """
    GET /unit_exam/{level_id}
    Gather a pool of questions from the given level (and optionally earlier ones),
    then return a random subset (e.g., 20).
    """
    user_id = 1  # Hardcoded

    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")

    # Collect all question objects from the content of this level
    all_questions = []
    for content in level.contents:
        all_questions.extend(content.questions)

    random.shuffle(all_questions)
    # Example: pick 20
    selected = all_questions[:20]

    data = []
    for q in selected:
        data.append({
            "question_id": q.id,
            "text": q.text,
            "options": [
                {"option_id": opt.id, "text": opt.text}
                for opt in q.options
            ]
        })

    return {"level_id": level_id, "questions": data}

@router.post("/{level_id}/submit")
def submit_unit_exam(level_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    POST /unit_exam/{level_id}/submit
    Expects JSON: { "answers": [ { "question_id": x, "option_id": y }, ... ] }
    Grades, checks pass/fail, unlocks next level, etc.
    """
    user_id = 1  # Hardcoded
    answers = payload.get("answers", [])
    correct_count = 0

    for ans in answers:
        question_id = ans["question_id"]
        chosen_option_id = ans["option_id"]
        chosen_option = db.query(Option).filter(Option.id == chosen_option_id).first()
        if chosen_option and chosen_option.is_correct:
            correct_count += 1
            uq = db.query(UserQuestionProgress).filter_by(
                user_id=user_id, question_id=question_id
            ).first()
            if not uq:
                uq = UserQuestionProgress(user_id=user_id, question_id=question_id)
                db.add(uq)
            uq.last_answer_correct = True
            uq.times_correct += 1
        else:
            uq = db.query(UserQuestionProgress).filter_by(
                user_id=user_id, question_id=question_id
            ).first()
            if not uq:
                uq = UserQuestionProgress(user_id=user_id, question_id=question_id)
                db.add(uq)
            uq.last_answer_correct = False
            uq.times_incorrect += 1

    db.commit()

    total_questions = len(answers)
    score = 0.0
    if total_questions > 0:
        score = correct_count / total_questions

    passed_exam = (score >= 0.8)  # Example threshold: 80%

    if passed_exam:
        message = f"Passed Level {level_id} exam. Next level unlocked!"
        # You'd typically mark the level completed for the user, etc.
    else:
        message = f"Failed Level {level_id} exam. Please review and try again."

    return {
        "correct": correct_count,
        "total": total_questions,
        "score": score,
        "passed": passed_exam,
        "message": message
    }
