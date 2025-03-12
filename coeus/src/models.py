from datetime import datetime
from src.database import db

class User(db.Model):
    """
    Represents a learner or user in the platform.
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # You could add relationships like:
    # contents_progress = db.relationship('UserContentProgress', backref='user', lazy=True)
    # questions_progress = db.relationship('UserQuestionProgress', backref='user', lazy=True)

class Level(db.Model):
    """
    Higher-level grouping of educational content (e.g., Unit, Chapter).
    """
    __tablename__ = "level"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    order_index = db.Column(db.Integer, nullable=True)
    # Relationship to content
    contents = db.relationship("Content", backref="level", lazy=True)

class Content(db.Model):
    """
    An individual educational unit (lesson/page).
    """
    __tablename__ = "content"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey("level.id"), nullable=True)
    order_index = db.Column(db.Integer, nullable=True)
    # Relationship to questions
    questions = db.relationship("Question", backref="content", lazy=True)

class Question(db.Model):
    """
    A multiple-choice question linked to a Content unit.
    """
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)

    # Relationship to multiple options
    options = db.relationship("Option", backref="question", lazy=True)

class Option(db.Model):
    """
    A possible answer to a question (multiple-choice).
    """
    __tablename__ = "option"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class UserContentProgress(db.Model):
    """
    Tracks a user's progress on a particular Content (lesson).
    - answered_count: total questions attempted
    - correct_count: total correct answers
    - passed: boolean indicating if user has met pass criteria
    """
    __tablename__ = "user_content_progress"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), primary_key=True)
    answered_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)

class UserQuestionProgress(db.Model):
    """
    Tracks a user's performance on each question for review and spaced repetition.
    - next_review_date: when the question is due for recall
    - times_correct / times_incorrect: counters
    """
    __tablename__ = "user_question_progress"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True)
    last_answer_correct = db.Column(db.Boolean, default=False)
    next_review_date = db.Column(db.DateTime, default=None)
    times_correct = db.Column(db.Integer, default=0)
    times_incorrect = db.Column(db.Integer, default=0)
