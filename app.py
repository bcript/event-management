from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
import sqlite3
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired


app = Flask(__name__)
app.secret_key = 'S3Cfnweas!elks#$!j23'
app.config['SECRET_KEY'] = 'W0rk1MS9ST$%#M!'
app.config['UPLOAD_FOLDER'] = 'static/worksheets'

class UploadFileForm(FlaskForm):
        file = FileField("File", validators=[InputRequired()])
        submit = SubmitField("Upload File")

# home page
@app.route('/', methods=['GET', 'POST'])
def home():
        if request.method == 'POST':

                # SQLite
                connection = sqlite3.connect('user_data.db')
                cursor = connection.cursor()

                # HTML Form
                email = request.form['email']
                password = request.form['password']

                print(email, password)

                # Query
                query = "SELECT email,password FROM users WHERE email='"+email+"' and password='"+password+"'"
                cursor.execute(query)

                results = cursor.fetchall()

                if len(results) == 0:
                        print('Incorrect credentials provided, try again.')
                else:
                        return render_template('logged_in.html')
        return render_template('index.html')

# register page
@app.route('/register', methods=['GET', 'POST'])
def register():
        if request.method == 'POST':
                email = request.form['email']
                password = request.form['password']
        
                # Connect to DB
                connection = sqlite3.connect('user_data.db')
                cursor = connection.cursor()

                # Check if email already exists
                cursor.execute('SELECT email FROM users WHERE email=?', (email,))
                if cursor.fetchone() is not None:
                        flash('Email already exists.', 'error')
                        connection.close()
                        return render_template('register.html')

                # Hash password for security purposes
                # to be added later

                cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
                connection.commit()
                connection.close()
                
                flash('Registration successful! You can now log in.', 'success')
                
        return render_template('register.html')

# worksheets page
@app.route('/worksheets', methods=['GET', 'POST'])
def worksheets():
        # check if user is logged in
        form = UploadFileForm()
        if form.validate_on_submit():
                file = form.file.data # grab the file
                file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
                return "File has been uploaded."
        return render_template('worksheets.html', form=form)

if __name__ == '__main__':
        app.run(debug=True, port=3333)
