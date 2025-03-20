import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import (
    Question, Option,
    UserContentProgress, UserQuestionProgress, SubmittedExam
)

router = APIRouter()

@router.get("/{content_id}")
def start_exam(content_id: int, db: Session = Depends(get_db), number_questions: int = 10):
    """
    GET /exam/{content_id}
    Return a number of random questions for the given content.
    """
    user_id = 1  # Hardcoded example

    questions = db.query(Question).filter(Question.content_id == content_id).all()
    random.shuffle(questions)
    selected_questions = questions[:number_questions]

    response_data = []
    for q in selected_questions:
        response_data.append({
            "question_id": q.id,
            "question_text": q.text,
            "options": [
                {"option_id": opt.id, "text": opt.text}
                for opt in q.options
            ]
        })

    return {
        "content_id": content_id,
        "questions": response_data
    }

@router.post("/{content_id}/submit")
def submit_exam(content_id: int, answers: SubmittedExam, db: Session = Depends(get_db)):
    """
    POST /exam/{content_id}/submit
    Expects JSON: { "answers": [ { "question_id": x, "option_id": y }, ... ] }
    Grades the exam, updates progress, checks pass/fail.
    """
    user_id = 1  # Hardcoded example

    # Extract answers list from payload
    submitted_answers = answers.get("answers", [])
    correct_count_this_attempt = 0

    # Grade each answer
    for ans in submitted_answers:
        question_id = ans["question_id"]
        chosen_option_id = ans["option_id"]

        chosen_option = db.query(Option).filter(Option.id == chosen_option_id).first()
        if chosen_option and chosen_option.is_correct:
            correct_count_this_attempt += 1
            # Update UserQuestionProgress
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

    # Update UserContentProgress
    ucp = db.query(UserContentProgress).filter_by(
        user_id=user_id, content_id=content_id
    ).first()
    if not ucp:
        ucp = UserContentProgress(user_id=user_id, content_id=content_id)
        db.add(ucp)

    ucp.answered_count += len(submitted_answers)
    ucp.correct_count += correct_count_this_attempt

    # Check pass criteria
    score_this_attempt = 0.0
    if len(submitted_answers) > 0:
        score_this_attempt = correct_count_this_attempt / len(submitted_answers)
    overall_correct_ratio = 0.0
    if ucp.answered_count > 0:
        overall_correct_ratio = ucp.correct_count / ucp.answered_count

    pass_80_percent = (score_this_attempt >= 0.8)
    pass_30_min = (ucp.answered_count >= 30)
    pass_50_ratio = (overall_correct_ratio >= 0.5)


    #Update UserContentProgress.passed and Content.available in db
    if pass_80_percent and pass_30_min and pass_50_ratio:
        ucp.passed = True
        next_ucp = db.query(UserContentProgress).filter_by(
        user_id=user_id, content_id=content_id+1
        ).first()
        next_ucp.available = True
    db.commit()

    return {
        "message": "Exam submitted",
        "correct_this_attempt": correct_count_this_attempt,
        "total_answered_so_far": ucp.answered_count,
        "total_correct_so_far": ucp.correct_count,
        "passed": ucp.passed
    }
