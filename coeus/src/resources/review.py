from flask_restful import Resource
from flask import request
from src.database import db
from src.models import (
    User, Question, Option,
    UserQuestionProgress
)

class ReviewResource(Resource):
    """
    GET /review
    or
    POST /review
    Handles the review process: serving failed questions and retesting them.
    """
    def get(self):
        # Hardcoded user_id=1
        user_id = 1
        # Find questions that the user last answered incorrectly
        # e.g., last_answer_correct=False
        failed_questions = UserQuestionProgress.query.filter_by(
            user_id=user_id, last_answer_correct=False
        ).all()

        # Return those questions (just an example)
        data = []
        for fq in failed_questions:
            question = Question.query.get(fq.question_id)
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

    def post(self):
        # Hardcoded user_id=1
        user_id = 1
        data = request.get_json()
        # data might be: { question_id, selected_option_id }

        question_id = data.get("question_id")
        selected_option_id = data.get("selected_option_id")

        # Check correctness
        chosen_option = Option.query.filter_by(id=selected_option_id).first()
        if not chosen_option:
            return {"message": "Invalid option selected."}, 400

        user_q_prog = UserQuestionProgress.query.filter_by(
            user_id=user_id, question_id=question_id
        ).first()

        if chosen_option.is_correct:
            # Mark question as correct, remove it from the 'failed' list
            user_q_prog.last_answer_correct = True
            user_q_prog.times_correct += 1
            # Possibly schedule next_review_date
        else:
            user_q_prog.last_answer_correct = False
            user_q_prog.times_incorrect += 1

        db.session.commit()

        # Return updated status for that question
        return {
            "question_id": question_id,
            "correct": chosen_option.is_correct
        }
