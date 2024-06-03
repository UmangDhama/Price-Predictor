from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import pickle
import json

app = Flask(__name__)

# Set the secret key for the session
app.secret_key = 'aeca33ed702baefe977ccd82eda43cb4'

# Load the trained model
with open('random_forest_regressor_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load the feature names and range values
df = pd.read_csv('Data.csv')
feature_names = df.columns[:-1].tolist()
feature_ranges = {
    feature: {
        'min': df[feature].min(),
        'max': df[feature].max()
    }
    for feature in feature_names
}

# Load user data from JSON file
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save user data to JSON file
def save_user_data(users):
    with open('user_data.json', 'w') as f:
        json.dump(users, f)

# User Database
users = load_user_data()

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'all':
            return render_template('predict_all.html', feature_names=feature_names, feature_ranges=feature_ranges)
        elif choice == 'select':
            return render_template('predict_select.html', feature_names=feature_names, feature_ranges=feature_ranges)
    return render_template('home.html')

@app.route('/predict_all', methods=['POST'])
def predict_all():
    if 'username' not in session:
        return redirect('/login')

    search_dict = {}
    for feature in feature_names:
        value = request.form.get(feature)
        try:
            value = float(value)
        except ValueError:
            return render_template('error.html')

        feature_range = feature_ranges.get(feature)
        if feature_range:
            min_val = feature_range['min']
            max_val = feature_range['max']
            if value < min_val or value > max_val:
                return render_template('predict_all.html', feature_names=feature_names, feature_ranges=feature_ranges, error_message=f"Value for {feature} is out of range.")
        search_dict[feature] = value

    search_df = pd.DataFrame(search_dict, index=[0])
    search_pred = model.predict(search_df)

    return render_template('result_all.html', prediction=search_pred[0], features=search_dict)


@app.route('/predict_all', methods=['GET'])
def show_predict_all():
    if 'username' not in session:
        return redirect('/login')

    return render_template('predict_all.html', feature_names=feature_names, feature_ranges=feature_ranges)


@app.route('/predict_select', methods=['GET', 'POST'])
def predict_select():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        selected_features = request.form.getlist('features')
        search_dict = {}

        for feature in selected_features:
            value = request.form.get(feature)

            if value is None or value == '':
                return render_template('predict_select.html', feature_names=feature_names, feature_ranges=feature_ranges, error_message=f"Please enter a value for {feature}.")

            try:
                value = float(value)
            except ValueError:
                return render_template('predict_select.html', feature_names=feature_names, feature_ranges=feature_ranges, error_message=f"Invalid input for {feature}. Please enter a valid number.")

            feature_range = feature_ranges.get(feature)
            if feature_range:
                min_val = feature_range['min']
                max_val = feature_range['max']
            else:
                min_val = float('-inf')
                max_val = float('inf')

            if value < min_val or value > max_val:
                return render_template('predict_select.html', feature_names=feature_names, feature_ranges=feature_ranges, error_message=f"Value for {feature} is out of range.")

            search_dict[feature] = value

        for feature in feature_names:
            if feature not in search_dict:
                min_val = feature_ranges[feature]['min']
                max_val = feature_ranges[feature]['max']
                random_value = np.random.uniform(min_val, max_val)
                search_dict[feature] = random_value

        search_df = pd.DataFrame(search_dict, index=[0])
        search_df = search_df.reindex(columns=feature_names, fill_value=0)
        search_pred = model.predict(search_df)

        if search_pred[0] < df['Price'].quantile(0.33):
            price_level = 'low'
        elif search_pred[0] > df['Price'].quantile(0.67):
            price_level = 'high'
        else:
            price_level = 'medium'

        selected_attributes = {k: v for k, v in search_dict.items() if k in selected_features}

        return render_template('result_select.html', prediction=round(search_pred[0], 2), price_level=price_level, attributes=selected_attributes)

    return render_template('predict_select.html', feature_names=feature_names, feature_ranges=feature_ranges, error_message='')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']

        if username in users:
            return render_template('signup.html', error_message='Username already exists. Please choose a different username.')

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Save user details
        users[username] = {
            'phone': phone,
            'password': hashed_password
        }
        save_user_data(users)

        session['username'] = username
        return redirect('/login')

    return render_template('signup.html', error_message='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            return redirect('/')

        return render_template('login.html', error_message='Invalid username or password.')

    return render_template('login.html', error_message='')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    user_data = users.get(username)
    if user_data:
        phone = user_data['phone']
        return render_template('profile.html', username=username, phone=phone)
    else:
        return render_template('profile.html', username=username, phone='')

if __name__ == '__main__':
    app.run(debug=True)
