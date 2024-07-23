from flask import Flask, render_template, request, flash
import sqlite3
app = Flask(__name__)
app.secret_key = 'S3Cfnweas!elks#$!j23'
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
                return render_template('index.html')
        return render_template('register.html')
if __name__ == '__main__':
        app.run(debug=True, port=3333)
