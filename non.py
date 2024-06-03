from flask import Flask, render_template, request, redirect, session
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

# Load the trained model
with open('random_forest_regressor_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load the feature names
df = pd.read_csv('DATA.csv')
feature_names = df.columns[:-1].tolist()

# User database (replace with your own database implementation)
users = {
    'john': {
        'phone': '1234567890',
        'password': 'password'
    },
    'jane': {
        'phone': '9876543210',
        'password': 'password'
    }
}


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        return render_template('home.html')

    return redirect('/signup')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Check if the username is already taken
        if username in users:
            return render_template('signup.html', error_message='Username already exists. Please choose a different username.')

        # Save the user details (replace with your own database storage logic)
        users[username] = {'phone': phone, 'password': password}

        session['username'] = username
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error_message='Invalid username or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/predict_all', methods=['POST'])
def predict_all():
    if 'username' not in session:
        return redirect('/login')

    # Rest of the code...


@app.route('/predict_select', methods=['GET', 'POST'])
def predict_select():
    if 'username' not in session:
        return redirect('/login')

    # Rest of the code...


if __name__ == '__main__':
    app.run(debug=True)
