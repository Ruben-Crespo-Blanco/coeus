import random
from flask_restful import Resource
from flask import request
from src.database import db
from src.models import (
    User, Level, Content, Question, Option,
    UserContentProgress, UserQuestionProgress
)

class UnitExamStartResource(Resource):
    """
    GET /unit_exam/<level_id>
    - Gather a pool of questions from all content in this level (and possibly earlier levels).
    - Return a random selection (e.g., 10-100 questions) based on the level difficulty.
    """
    def get(self, level_id):
        # Hardcoded user_id=1
        user_id = 1

        # Example: get the current level
        current_level = Level.query.get_or_404(level_id)

        # Gather questions from all Content in this level
        all_content_ids = [c.id for c in current_level.contents]
        questions = Question.query.filter(Question.content_id.in_(all_content_ids)).all()

        # You could also include previous levels' questions at some ratio.
        # For simplicity, we just use the current level.
        random.shuffle(questions)
        # Let’s say this level’s exam is 20 questions
        selected_questions = questions[:20]

        data = []
        for q in selected_questions:
            data.append({
                "question_id": q.id,
                "text": q.text,
                "options": [{"id": opt.id, "text": opt.text} for opt in q.options]
            })

        return {"level_id": level_id, "questions": data}

class UnitExamSubmitResource(Resource):
    """
    POST /unit_exam/<level_id>/submit
    - User answers the unit exam.
    - Logic: grade, determine pass/fail, possibly unlock next level or prompt for review.
    """
    def post(self, level_id):
        # Hardcoded user_id=1
        user_id = 1
        data = request.get_json()
        # data might be: { answers: [ {question_id, option_id}, ... ] }

        answers = data.get("answers", [])
        correct_count = 0

        for ans in answers:
            question_id = ans["question_id"]
            chosen_option_id = ans["option_id"]
            chosen_option = Option.query.filter_by(id=chosen_option_id).first()

            if chosen_option and chosen_option.is_correct:
                correct_count += 1
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
            else:
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

        db.session.commit()

        # Example pass/fail condition: 80% correct
        total_questions = len(answers)
        score = 0.0
        if total_questions > 0:
            score = correct_count / total_questions

        passed_exam = (score >= 0.8)

        if passed_exam:
            # In your full logic, you'd mark the level as completed,
            # unlock the next level, etc.
            message = f"You passed the Level {level_id} exam!"
        else:
            # Possibly queue up a review session with the missed questions
            message = f"You failed the Level {level_id} exam. Please review and retry."

        return {
            "correct": correct_count,
            "total": total_questions,
            "score": score,
            "passed": passed_exam,
            "message": message
        }
