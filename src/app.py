from flask import Flask, jsonify, render_template, request, url_for, redirect , session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from models import *
from functools import wraps
import requests
import os

load_dotenv()

api_key = os.getenv("WEATHER_KEY")
print(api_key)
base_url = "https://api.openweathermap.org/data/2.5/weather"

dbUser = os.getenv("db_user")
dbPassword = os.getenv("db_password")
dbHost = os.getenv('db_host')
dbPort = os.getenv('db_port')
database = os.getenv('database')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{dbUser}:{dbPassword}@{dbHost}:{dbPort}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ------- Creating the login required right here to make the application safer --------- #

def login_required(route_func):
    @wraps(route_func)

    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        
        return route_func(*args,**kwargs)
    return wrapper


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form.to_dict()

        user = User.query.filter_by(email=data.get('email')).first()
        username = User.query.filter_by(username=data.get('username')).first()

        if user:
            print("User already exists")
            return redirect(url_for('signup'))

        if username:
            print("Username already in use")
            return redirect(url_for('signup'))

        try:
            newUser = User(
                email=data['email'],
                username=data['username'],
                password=generate_password_hash(data['password'])
            )
            db.session.add(newUser)
            db.session.commit()

            return redirect(url_for('login'))

        except Exception as e:
            print("Error:", e)
            return redirect(url_for('signup'))

    return render_template('signup.html')


@app.route('/', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        data = request.form.to_dict()

        user = User.query.filter_by(email=data.get('email')).first()

        if user and check_password_hash(user.password, data.get('password')):
            session["user"] = user.email
            return redirect(url_for('main'))

        print("Invalid login")
        return redirect(url_for('login'))

    return render_template('index.html')


@app.route('/weather-api', methods=['POST'])
@login_required
def weatherApp():
    city = request.form.get("city").strip().lower() # Collecting the city's name in lower case and without accents
    print("City received:", city)

    url = f"{base_url}?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    print("Status code:", response.status_code)
    print("Response:", response.text)

    if response.status_code != 200:
        return jsonify({'error': 'City not found'}), 404

    data = response.json()
    temp = data['main']['temp']

    return jsonify({
        'city': city.title(),
        'temperature': temp
    })


@app.route('/main')
@login_required
def main():
    return render_template('main.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)