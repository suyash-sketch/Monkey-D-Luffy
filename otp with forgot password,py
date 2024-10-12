from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import smtplib
import random
import string
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="T1mex@_o6/2018",
    database="miniproject"
)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

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
    return render_template('new-signup.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthdate = request.form['birthdate']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        otp = generate_otp()
        send_otp(email, otp)
        session['user_data'] = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'birthdate': birthdate,
            'gender': gender,
            'email': email,
            'password': password,
            'otp': otp
        }
        return redirect(url_for('verify'))
    return render_template('new-signup.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        user_data = session.get('user_data')
        if user_data and user_data['otp'] == entered_otp:
            cursor = db.cursor()
            sql = "INSERT INTO users (username, first_name, last_name, birthdate, gender, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (user_data['username'], user_data['first_name'], user_data['last_name'], user_data['birthdate'], user_data['gender'], user_data['email'], user_data['password'])
            cursor.execute(sql, val)
            db.commit()
            session.pop('user_data', None)
            return "Account created and verified successfully!"
        else:
            return "Invalid OTP. Please try again."
    return render_template('new-verify.html')

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
    return render_template('new-signin.html')

@app.route('/login')
def login_page():
    return render_template('new-signin.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        step = request.form.get('step')
        if step == '1':
            email = request.form['email']
            username = request.form['username']
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND email = %s", (username, email))
            user = cursor.fetchone()
            if user:
                otp = generate_otp()
                send_otp(email, otp)
                session['reset_data'] = {
                    'username': username,
                    'email': email,
                    'otp': otp
                }
                return render_template('forgot-password.html', step='2')
            else:
                return "No user found with the provided username and email."
        elif step == '2':
            entered_otp = request.form['otp']
            reset_data = session.get('reset_data')
            if reset_data and reset_data['otp'] == entered_otp:
                return render_template('forgot-password.html', step='3')
            else:
                return "Invalid OTP. Please try again."
        elif step == '3':
            new_password = request.form['new_password']
            reset_data = session.get('reset_data')
            if reset_data:
                cursor = db.cursor()
                sql = "UPDATE users SET password = %s WHERE username = %s AND email = %s"
                val = (new_password, reset_data['username'], reset_data['email'])
                cursor.execute(sql, val)
                db.commit()
                session.pop('reset_data', None)
                return "Password reset successfully!"
    return render_template('forgot-password.html', step='1')

if __name__ == '__main__':
    app.run(debug=True)
