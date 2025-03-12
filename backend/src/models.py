from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

class Level(Base):
    __tablename__ = "level"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    order_index = Column(Integer, nullable=True)

    contents = relationship("Content", back_populates="level")

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=True)
    level_id = Column(Integer, ForeignKey("level.id"), nullable=True)
    order_index = Column(Integer, nullable=True)

    level = relationship("Level", back_populates="contents")
    questions = relationship("Question", back_populates="content")

class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    text = Column(Text, nullable=False)

    content = relationship("Content", back_populates="questions")
    options = relationship("Option", back_populates="question")

class Option(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="options")

class UserContentProgress(Base):
    __tablename__ = "user_content_progress"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    content_id = Column(Integer, ForeignKey("content.id"), primary_key=True)
    answered_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    passed = Column(Boolean, default=False)

class UserQuestionProgress(Base):
    __tablename__ = "user_question_progress"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("question.id"), primary_key=True)
    last_answer_correct = Column(Boolean, default=False)
    next_review_date = Column(DateTime, default=None)
    times_correct = Column(Integer, default=0)
    times_incorrect = Column(Integer, default=0)
