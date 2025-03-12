from flask_restful import Resource
from flask import request, jsonify
from datetime import datetime
from src.database import db
from src.models import (
    User, Content, UserContentProgress, UserQuestionProgress, Question
)

class NextContentResource(Resource):
    """
    GET /content/next
    - Work queue logic in order: remember -> review -> test -> new content
    - If none are pending, serve next unlocked content.
    """
    def get(self):
        # In a real app, identify the current user from auth
        # Hardcoded user_id=1 for example
        user_id = 1

        # TODO: 1) Check if user has questions due for recall
        #       2) Check if user has pending reviews from failed questions
        #       3) If user has unpassed content, serve an exam
        #       4) Else, serve new content if unlocked

        # For demonstration, just returning a placeholder:
        return {
            "message": (
                "Next content or next step in the queue goes here. "
                "Implement spaced repetition, review checks, exam gating, etc."
            )
        }

class ContentResource(Resource):
    """
    GET /content/<content_id>
    Return the details of a specific content unit.
    """
    def get(self, content_id):
        content = Content.query.get_or_404(content_id)
        return {
            "id": content.id,
            "title": content.title,
            "body": content.body,
            "level_id": content.level_id
        }
