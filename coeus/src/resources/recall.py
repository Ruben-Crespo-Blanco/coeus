from datetime import datetime, timedelta
from flask_restful import Resource
from flask import request
from src.database import db
from src.models import (
    User, Question, Option,
    UserQuestionProgress
)

class RecallResource(Resource):
    """
    GET /remember
    Fetch a set of previously learned questions that are due for spaced repetition review.
    """
    def get(self):
        # Hardcoded user_id=1
        user_id = 1
        now = datetime.utcnow()

        # Find questions whose next_review_date <= now
        due_questions = UserQuestionProgress.query.filter(
            UserQuestionProgress.user_id == user_id,
            UserQuestionProgress.next_review_date != None,
            UserQuestionProgress.next_review_date <= now
        ).all()

        response_data = []
        for uq in due_questions:
            q = Question.query.get(uq.question_id)
            if q:
                response_data.append({
                    "question_id": q.id,
                    "text": q.text,
                    "options": [
                        {"option_id": opt.id, "text": opt.text}
                        for opt in q.options
                    ]
                })

        return {"due_recall_questions": response_data}

class RecallSubmitResource(Resource):
    """
    POST /remember/submit
    User submits answers to recall questions. The system updates correctness
    and reschedules next_review_date based on spaced repetition.
    """
    def post(self):
        # Hardcoded user_id=1
        user_id = 1
        data = request.get_json()
        # data: { answers: [ { question_id, option_id }, ... ] }

        answers = data.get("answers", [])
        now = datetime.utcnow()

        for ans in answers:
            question_id = ans["question_id"]
            option_id = ans["option_id"]

            chosen_option = Option.query.filter_by(id=option_id).first()
            user_q_prog = UserQuestionProgress.query.filter_by(
                user_id=user_id, question_id=question_id
            ).first()

            if not user_q_prog:
                # If somehow not in DB, create an entry
                user_q_prog = UserQuestionProgress(
                    user_id=user_id,
                    question_id=question_id
                )
                db.session.add(user_q_prog)

            if chosen_option and chosen_option.is_correct:
                user_q_prog.last_answer_correct = True
                user_q_prog.times_correct += 1
                # Example simple spacing: add 7 days every time
                # Real logic might be more sophisticated
                user_q_prog.next_review_date = now + timedelta(days=7)
            else:
                user_q_prog.last_answer_correct = False
                user_q_prog.times_incorrect += 1
                # Retry sooner if failed, e.g. 1 day
                user_q_prog.next_review_date = now + timedelta(days=1)

        db.session.commit()

        return {"message": "Recall answers submitted and next review scheduled."}
