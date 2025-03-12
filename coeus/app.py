from flask import Flask
from flask_restful import Api
from config import Config
from src.database import db

# Import resource classes from our 'resources' package
from src.resources.content import NextContentResource, ContentResource
from src.resources.exam import ExamStartResource, ExamSubmitResource
from src.resources.review import ReviewResource
from src.resources.recall import RecallResource, RecallSubmitResource
from src.resources.unit_exam import UnitExamStartResource, UnitExamSubmitResource

def create_app(config_class=Config):
    """
    Application factory pattern: create and configure a Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database with Flask app
    db.init_app(app)

    # Create a Flask-RESTful API and add resources/endpoints
    api = Api(app)

    # Content endpoints
    api.add_resource(NextContentResource, "/content/next")           # GET next content (or next step in queue)
    api.add_resource(ContentResource, "/content/<int:content_id>")   # GET specific content details

    # Exam endpoints
    api.add_resource(ExamStartResource, "/exam/<int:content_id>")        # GET: start (fetch) exam questions
    api.add_resource(ExamSubmitResource, "/exam/<int:content_id>/submit") # POST: submit answers to exam

    # Review endpoints
    api.add_resource(ReviewResource, "/review") # GET/POST for review cycle

    # Recall (spaced repetition) endpoints
    api.add_resource(RecallResource, "/remember")         # GET: fetch recall questions
    api.add_resource(RecallSubmitResource, "/remember/submit")  # POST: submit recall answers

    # Unit exam endpoints
    api.add_resource(UnitExamStartResource, "/unit_exam/<int:level_id>")         # GET: start level exam
    api.add_resource(UnitExamSubmitResource, "/unit_exam/<int:level_id>/submit") # POST: submit level exam

    return app

if __name__ == "__main__":
    # Run the app with default config
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
