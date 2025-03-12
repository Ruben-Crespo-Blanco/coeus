import random
from flask_restful import Resource
from flask import request
from src.database import db
from src.models import (
    User, Content, Question, Option,
    UserContentProgress, UserQuestionProgress
)

class ExamStartResource(Resource):
    """
    GET /exam/<content_id>
    Fetch 10 random questions related to the given content.
    """
    def get(self, content_id):
        # Hardcoded user_id=1 for demonstration
        user_id = 1

        # Get all questions for this content
        all_questions = Question.query.filter_by(content_id=content_id).all()
        # Randomly pick up to 10 (or fewer if content has fewer)
        random.shuffle(all_questions)
        selected_questions = all_questions[:10]

        # Prepare response
        exam_questions = []
        for q in selected_questions:
            exam_questions.append({
                "question_id": q.id,
                "question_text": q.text,
                "options": [
                    {"option_id": opt.id, "text": opt.text}
                    for opt in q.options
                ]
            })

        return {
            "content_id": content_id,
            "questions": exam_questions
        }

class ExamSubmitResource(Resource):
    """
    POST /exam/<content_id>/submit
    Accepts the user's answers, grades them, updates progress,
    and checks pass/fail conditions for that content.
    """
    def post(self, content_id):
        # Hardcoded user_id=1 for demonstration
        user_id = 1
        data = request.get_json()

        # data is expected to have: { answers: [ {question_id, option_id}, ... ] }

        answers = data.get("answers", [])
        correct_count_this_attempt = 0

        # For each submitted answer, check correctness
        for ans in answers:
            question_id = ans["question_id"]
            chosen_option_id = ans["option_id"]
            # Find that Option in DB:
            chosen_option = Option.query.filter_by(id=chosen_option_id).first()
            if chosen_option and chosen_option.is_correct:
                correct_count_this_attempt += 1
                # Update user-question progress
                uq = UserQuestionProgress.query.filter_by(
                    user_id=user_id, question_id=question_id
                ).first()
                if not uq:
                    uq = UserQuestionProgress(
                        user_id=user_id, question_id=question_id
                    )
                    db.session.add(uq)
                uq.last_answer_correct = True
                uq.times_correct += 1
                # Spaced repetition logic: schedule next review further out, etc.
                # TODO: set uq.next_review_date based on spaced repetition formula
            else:
                # Mark question as incorrect
                uq = UserQuestionProgress.query.filter_by(
                    user_id=user_id, question_id=question_id
                ).first()
                if not uq:
                    uq = UserQuestionProgress(
                        user_id=user_id, question_id=question_id
                    )
                    db.session.add(uq)
                uq.last_answer_correct = False
                uq.times_incorrect += 1
                # Possibly schedule an earlier review, etc.

        # Update user content progress
        ucp = UserContentProgress.query.filter_by(
            user_id=user_id, content_id=content_id
        ).first()
        if not ucp:
            ucp = UserContentProgress(user_id=user_id, content_id=content_id)
            db.session.add(ucp)

        # Increment the answered_count by the number of questions answered
        ucp.answered_count += len(answers)
        ucp.correct_count += correct_count_this_attempt

        # Check if content can be marked as passed
        # Conditions described:
        #   1) Score >= 80% on this attempt? (8 out of 10)
        #   2) At least 30 cumulative questions answered
        #   3) Overall correctness >= 50%
        score_this_attempt = 0.0
        if len(answers) > 0:
            score_this_attempt = correct_count_this_attempt / len(answers)

        overall_correct_ratio = 0.0
        if ucp.answered_count > 0:
            overall_correct_ratio = ucp.correct_count / ucp.answered_count

        # Attempt threshold check
        pass_80_percent = (score_this_attempt >= 0.8)
        # Minimun answered
        pass_30_minimum = (ucp.answered_count >= 30)
        # Overall ratio
        pass_50_percent = (overall_correct_ratio >= 0.5)

        # Mark content passed if all conditions are satisfied
        if pass_80_percent and pass_30_minimum and pass_50_percent:
            ucp.passed = True

        db.session.commit()

        # Return exam result
        return {
            "message": "Exam submitted.",
            "correct_this_attempt": correct_count_this_attempt,
            "total_answered_so_far": ucp.answered_count,
            "total_correct_so_far": ucp.correct_count,
            "passed": ucp.passed
        }
