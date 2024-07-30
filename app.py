from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'W0rk1MS9ST$%#M!'

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
        event_date = request.form.get('date')
        event_time = request.form.get('time')
        event_desc = request.form.get('event_description')
        
        # Combine date and time
        start_datetime = f"{event_date}T{event_time}"
        
        # Assume event duration is 1 hour for this example
        end_datetime = datetime.fromisoformat(start_datetime) + timedelta(hours=1)
        end_datetime = end_datetime.isoformat()

        db = get_db()
        db.execute('INSERT INTO events (user_id, name, start_date, end_date, description) VALUES (?, ?, ?, ?, ?)',
                   (session['user_id'], event_name, start_datetime, end_datetime, event_desc))
        db.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        return render_template('eventcreation.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

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
        event_list.append({
            'id': event['id'],
            'title': event['name'],
            'start': event['start_date'],
            'end': event['end_date'],
            'description': event['description']
        })
    
    return jsonify(event_list)

if __name__ == '__main__':
    app.run(debug=True, port=3333)
