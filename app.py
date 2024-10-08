from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xxx'

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    submit = SubmitField("Register")

def get_db():
    db = sqlite3.connect('user_data.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, start_date TEXT, end_date TEXT, description TEXT, FOREIGN KEY (user_id) REFERENCES users (id))')
    db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER, description TEXT, completed BOOLEAN, FOREIGN KEY (event_id) REFERENCES events (id))')
    db.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('index.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        db = get_db()
        if db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            flash('Email already registered.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            db.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('index'))
    
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/event-creation', methods=['GET', 'POST'])
@login_required
def event_creation():
    if request.method == 'POST':
        event_name = request.form.get('name')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')
        event_desc = request.form.get('event_description')
        
        # Check if all date and time fields are provided
        if start_date and start_time and end_date and end_time:
            # Combine date and time for start and end
            start_datetime = f"{start_date}T{start_time}"
            end_datetime = f"{end_date}T{end_time}"
        else:
            flash('Please provide both start and end date and time for the event.', 'error')
            return redirect(url_for('event_creation'))

        try:
            db = get_db()
            db.execute('INSERT INTO events (user_id, name, start_date, end_date, description) VALUES (?, ?, ?, ?, ?)',
                       (session['user_id'], event_name, start_datetime, end_datetime, event_desc))
            db.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            db.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            db.close()

    return render_template('eventcreation.html')

@app.route('/calendar')
@login_required
def calendar():
    return render_template('dashboard.html')

@app.route('/events')
@login_required
def events():
    db = get_db()
    events = db.execute('SELECT id, name, start_date, end_date, description FROM events WHERE user_id = ?', (session['user_id'],)).fetchall()
    
    event_list = []
    for event in events:
        tasks = db.execute('SELECT id, description, completed FROM tasks WHERE event_id = ?', (event['id'],)).fetchall()
        event_list.append({
            'id': event['id'],
            'title': event['name'],
            'start': event['start_date'],
            'end': event['end_date'],
            'description': event['description'],
            'tasks': [{'id': task['id'], 'description': task['description'], 'completed': task['completed']} for task in tasks]
        })
    
    return jsonify(event_list)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    event_id = request.form.get('event_id')
    task_description = request.form.get('task_description')
    
    db = get_db()
    db.execute('INSERT INTO tasks (event_id, description, completed) VALUES (?, ?, ?)',
               (event_id, task_description, False))
    db.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=3333)
