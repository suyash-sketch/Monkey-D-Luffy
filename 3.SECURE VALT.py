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
    password="your_password",
    database="miniproject"
)

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp(email, otp):
    sender_email = "www.securevalt@gmail.com"
    sender_password = "pjsi htiy taax iybz"
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
            return 'success'
        return render_template('new-signin.html')
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
            session['first_name'] = user[1]  # Assuming 1st index is first_name
            session['last_name'] = user[2]   # Assuming 2nd index is last_name
            session['gender'] = user[3]       # Assuming 4th index is gender
            session['birthdate'] = user[4]   # Assuming 3rd index is birthdate
            session['email'] = user[5]       # Assuming 5th index is email
            return render_template('homescreen.html',username=username)
        else:
            return render_template('new-signin.html', message='Invalid username or password')
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

@app.route('/get_users', methods=['GET'])
def get_users():
    cursor = db.cursor()
    cursor.execute("SELECT first_name, last_name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('db-index.html', users=users)

@app.route('/archive', methods=['POST'])
def archive_entry():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    app_name = request.form['app_name']
    a_username = request.form['a_username']
    a_password = request.form['a_password']
    r_username = session['username']
                        
    cursor = db.cursor()
    sql = "INSERT INTO accounts (r_username, app_name, a_username, a_password) VALUES (%s, %s, %s, %s)"
    val = (r_username, app_name, a_username, a_password)
    cursor.execute(sql, val)
    db.commit()
    return render_template('archive.html', message='DATA added successfully')

@app.route('/archive')
def archive_form():
    if 'username' not in session:
        redirect(url_for('login_page'))
    return render_template('archive.html')

@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve_data():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        user_data = session.get('user_data')
        if user_data and user_data['otp'] == entered_otp:
            r_username = session['username']
            cursor = db.cursor()
            sql = "SELECT app_name, a_username, a_password FROM accounts WHERE r_username = %s"
            cursor.execute(sql, (r_username,))
            data = cursor.fetchall()
            return render_template('retrieve.html', data=data, message='OTP Verified successfully Welcome')
        else:
            return "Invalid OTP. Please try again."

    # For GET request, generate and send OTP
    user_email = session.get('email')
    otp = generate_otp()
    send_otp(user_email, otp)
    session['user_data'] = {'otp': otp}
    return render_template('retrieve-verify.html')
    


@app.route('/delete', methods=['POST', 'GET'])
def delete_data():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        app_name = request.form['app_name']
        a_username = request.form['a_username']
        a_password = request.form['a_password']

        cursor = db.cursor()
        sql = "DELETE FROM accounts WHERE r_username = %s AND app_name = %s AND a_username = %s AND a_password = %s"
        val = (session['username'], app_name, a_username, a_password)
        cursor.execute(sql, val)
        db.commit()
        
        return render_template('archive.html', message='Data deleted successfully')

    return render_template('delete.html')

@app.route('/setting')
def setting_page():
    return render_template('setting.html')

@app.route('/profile')
def profile_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('profileinsight.html', first_name=session['first_name'], last_name=session['last_name'], username=session['username'], birthdate=session['birthdate'], gender=session['gender'], email=session['email'])
    

@app.route('/subscription')
def subscription_page():
    return render_template('subscription.html')

@app.route('/aboutus')
def aboutus_page():
    return render_template('aboutus.html')

@app.route('/home')
def homescreen():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('homescreen.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)

