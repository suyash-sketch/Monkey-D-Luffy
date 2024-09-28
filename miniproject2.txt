from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import smtplib
import random
import string
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # replace with your MySQL username
    password="T1mex@_o6/2018",  # replace with your MySQL password
    database="miniproject"
)

# Function to generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function to send OTP via email
def send_otp(email, otp):
    sender_email = "khandagalesuyash05@gmail.com"
    sender_password = "kmnr taqd pxsv sxlj"
    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}"

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message)

@app.route('/')
def form():
    return render_template('signup.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    logging.info(f"Request method: {request.method}")
    logging.info(f"Request URL: {request.url}")
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']

        otp = generate_otp()
        send_otp(email, otp)

        # Store user data in session
        session['user_data'] = {
            'username': username,
            'name': name,
            'birthdate': birthdate,
            'gender': gender,
            'email': email,
            'password': password,
            'otp': otp
        }
        return redirect(url_for('verify'))
    else:
        return render_template('signup.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        user_data = session.get('user_data')

        if user_data and user_data['otp'] == entered_otp:
            cursor = db.cursor()
            sql = "INSERT INTO users (username, name, birthdate, gender, email, password) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (user_data['username'], user_data['name'], user_data['birthdate'], user_data['gender'], user_data['email'], user_data['password'])
            cursor.execute(sql, val)
            db.commit()

            # Clear session data
            session.pop('user_data', None)

            return "Account created and verified successfully!"
        else:
            return "Invalid OTP. Please try again."

    return render_template('verify2.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            return "Login successful! Welcome, " + username
        else:
            return render_template('invalid.html')

    return render_template('signin.html')

@app.route('/login')
def login_page():
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)
