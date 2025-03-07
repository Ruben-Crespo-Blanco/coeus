from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)

# A secret key is needed for session management
app.secret_key = os.getenv('SECRET_KEY')


# For development, let's use an SQLite database file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'coeus.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------
# Models
# ---------------------------------------------------

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed in real app

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

# Many-to-many relationship: Users <-> Courses
# We'll create an enrollment table
enrollment_table = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In real app, hash password

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists!"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In real app, compare hashed password

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Store user in session
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    return redirect(url_for('index'))

@app.route('/courses')
def list_courses():
    """List all courses."""
    courses = Course.query.all()
    return render_template('course_list.html', courses=courses)

@app.route('/courses/create', methods=['GET', 'POST'])
def create_course():
    """Create a new course."""
    # Optional: Check if user is logged in and maybe if user is an instructor
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        new_course = Course(title=title, description=description)
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for('list_courses'))

    return render_template('create_course.html')

# ---------------------------------------------------
# Database initialization
# ---------------------------------------------------

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# ---------------------------------------------------
# Run the app
# ---------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
