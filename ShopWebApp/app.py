from datetime import datetime
import requests, json, os, psycopg2
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort , g
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy, sqlalchemy_utils

error_type = ''
error = ''


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRECT_KEY','@unitedremote@2019')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vsamkirghjtirg:fa8c6e0206676c2706036222a797f73e3468a9ad849912a1107e2435a8abad83@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d7ijjntbq52n4g'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
wsgi_app = app.wsgi_app
db = SQLAlchemy(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


api_key = '8725c6e9248c510a9869fc8ecca153a3'
"""
def get_location():
    URL = 'http://api.ipstack.com/'+ request.remote_addr +'?access_key=' + api_key + '&output=json'
    r = requests.get(URL)
    position = json.loads(r.text)
    lat = position['latitude']
    ilong = position['longitude']
    loc = str(lat) + ',' + str(ilong)
    print(loc)
    return loc
"""

url = 'https://api.foursquare.com/v2/venues/explore'

"""
def get_places():
    resp = requests.get(url=url, params=params)
    data = resp.json()
    places = []
    response = data['response']
    for group in response['groups']:
        for item in group['items']:
            places_holder = {}
            venue = item['venue']
            place_id = venue['id']
            place_name = venue['name']
            location = venue['location']
            formatted_address = location['formattedAddress']
            if str(place_name) not in places:
                places_holder['name'] = place_name
            for icons in venue['categories']:
                photo = icons['icon']
                prefix = photo['prefix']
                suffix = photo['suffix']
                place_photo = prefix + suffix
                places_holder['photo'] = place_photo
            places_holder['type'] = 'Shop'
            places_holder['location'] = formatted_address
            places_holder['id'] = place_id
            places.append(places_holder)
    return places
"""

@app.route('/Search', methods=['POST', 'GET'])
@login_required
def Search():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    URL = 'http://api.ipstack.com/'+ ip_address +'?access_key=' + api_key + '&output=json'
    r = requests.get(URL)
    position = json.loads(r.text)
    lat = position['latitude']
    ilong = position['longitude']
    loc = str(lat) + ',' + str(ilong)
    print(loc)
    params = dict(
        client_id='VQ0LMBJRKFVDNFOSIIGB2K3Y5LJPJAY2BXDGZCYY5VBVL5D1',
        client_secret='MZ5DBZXGX1X1DS0KVHCA5E5NCU0H0YZCISYFZ35VU0OV1YGI',
        v='20180323',
        ll=loc,
        query='shop',
        limit=10
    )
    def get_places():
        resp = requests.get(url=url, params=params)
        data = resp.json()
        places = []
        response = data['response']
        for group in response['groups']:
            for item in group['items']:
                places_holder = {}
                venue = item['venue']
                place_id = venue['id']
                place_name = venue['name']
                location = venue['location']
                formatted_address = location['formattedAddress']
                if str(place_name) not in places:
                    places_holder['name'] = place_name
                for icons in venue['categories']:
                    photo = icons['icon']
                    prefix = photo['prefix']
                    suffix = photo['suffix']
                    place_photo = prefix + suffix
                    places_holder['photo'] = place_photo
                places_holder['type'] = 'Shop'
                places_holder['location'] = formatted_address
                places_holder['id'] = place_id
                places.append(places_holder)
        return places
    return render_template('Search.html', places = get_places())


@app.before_request
def before_request():
    psycopg2.connect('postgres://vsamkirghjtirg:fa8c6e0206676c2706036222a797f73e3468a9ad849912a1107e2435a8abad83@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d7ijjntbq52n4g')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    #todos = db.relationship('Todo' , backref='user',lazy='dynamic')

    def __init__(self , username ,password , email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

#if not database_exists(engine.url):
    #create_database(engine.url)
#print(engine.url)

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    email = request.form['email']
    password = request.form['password']
    registered_user = User.query.filter_by(email=email).first()
    if registered_user and registered_user.check_password(password):
        flash('Email or Password already registered','error')
        return redirect(url_for('login'))

    user = User(request.form['username'] , password, email)
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form['email']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = User.query.filter_by(email=email).first()
    if registered_user is None:
        flash('Email is invalid' , 'error')
        return redirect(url_for('login'))
    if not registered_user.check_password(password):
        flash('Password is invalid','error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('Search'))


@app.route('/Logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Dashboard')
def Dashboard():
    return render_template('Dashboard.html')

@app.route('/about')
def About():
    return render_template('About.html')

@app.route('/Contact')
def Contact():
    return  render_template('Contact.html')

@app.route('/password_recovery')
@login_required
def password_recovery():
    return render_template('password_recovery.html')
