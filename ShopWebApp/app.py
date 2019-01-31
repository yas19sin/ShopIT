from datetime import datetime
import requests, json, os, psycopg2
from flask import Flask, session, request, flash, url_for, redirect, render_template, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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
url = 'https://api.foursquare.com/v2/venues/explore'


def get_places(params):
    print('url')
    print(url)
    print('params')
    print(params)
    resp = requests.get(url=url, params=params)
    print('response')
    print(resp)
    data = resp.json()
    places = []
    photo_size = '300x500'
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
                place_photo = prefix + photo_size + suffix
                places_holder['photo'] = place_photo
            places_holder['type'] = 'Shop'
            places_holder['location'] = formatted_address
            places_holder['id'] = place_id
            places.append(places_holder)
    print('places')
    print(places)
    return places


@app.route('/Search', methods=['POST', 'GET'])
@login_required
def Search():
    if request.method == 'POST':
        ip_address = '196.75.219.136'#request.access_route[0]
        urls = 'http://api.ipstack.com/' + ip_address + '?access_key=' + api_key +'&output=json'
        data = requests.get(urls)
        position = data.json()
        lat = position['latitude']
        ilong = position['longitude']
        loc = str(lat) + ',' + str(ilong)
        params = dict(
            client_id='VQ0LMBJRKFVDNFOSIIGB2K3Y5LJPJAY2BXDGZCYY5VBVL5D1',
            client_secret='MZ5DBZXGX1X1DS0KVHCA5E5NCU0H0YZCISYFZ35VU0OV1YGI',
            v='20180323',
            ll=loc,
            query='Shop,Shops',
            limit=25
        )
        return render_template('Search.html', places = get_places(params))
    return render_template('Search.html')


@app.before_request
def before_request():
    psycopg2.connect('postgres://vsamkirghjtirg:fa8c6e0206676c2706036222a797f73e3468a9ad849912a1107e2435a8abad83@ec2-54-75-230-41.eu-west-1.compute.amazonaws.com:5432/d7ijjntbq52n4g')
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), index=True)
    password = db.Column('password', db.String(250))
    email = db.Column('email', db.String(50), unique=True, index=True)

    def __init__(self, username, password, email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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


class Places(db.Model):
    __tablename__ = "Places"
    ids = db.Column('id', db.String, unique=True, primary_key=True)
    name = db.Column('name', db.String, unique=True, index=True)
    location = db.Column('location', db.String, index=True)
    photo = db.Column('photo', db.String, unique=True, index=True)
    types = db.Column('type', db.String)

    def __init__(self, ids, name, location, photo, types):
        self.ids = ids
        self.name = name
        self.location = location
        self.photo = photo
        self.types = types

    def __repr__(self):
        return '<place name %r>' % (self.name)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    email = request.form['email']
    password = request.form['password']
    registered_user = User.query.filter_by(email=email).first()
    if registered_user and registered_user.check_password(password):
        flash('Email or Password already registered', 'error')
        return redirect(url_for('login'))

    user = User(request.form['username'], password, email)
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
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
        flash('Email is invalid', 'error')
        return redirect(url_for('login'))
    if not registered_user.check_password(password):
        flash('Password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user, remember=remember_me)
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


@app.route('/Dashboard')
@login_required
def Dashboard():
    places = db.session.query(Places).all()
    placee = []
    for place in places:
        Place = {}
        Place['id'] = place.ids
        Place['name'] = place.name
        Place['location'] = place.location
        Place['photo'] = place.photo
        Place['type'] = place.types
        placee.append(Place)
    return render_template('Dashboard.html', Place=placee)


@app.route('/like', methods=['GET'])
@login_required
def like():
    place = {}
    ids = request.args.get('id')
    name = str(request.args.get('name'))
    location = str(request.args.get('location'))
    photo = str(request.args.get('photo'))
    types = str(request.args.get('type'))
    if ids is None:
        return flash('There is no place to be added', 'error')

    place['id'] = ids
    place['name'] = name
    place['location'] = location
    place['photo'] = photo
    place['types'] = types

    already_saved = Places.query.filter_by(ids=ids, name=name, location=location, photo=photo, types=types).all()
    if already_saved:
        flash('already added to Dashboard', 'error')
        return render_template('Dashboard.html')

    places = Places(ids, name, location, photo, types)
    db.session.add(places)
    db.session.commit()
    flash('Place Successfully Added to your Dashboard')
    return render_template('Dashboard.html', place=place)


@app.route('/dislike')
@login_required
def Dislike():
    ids = request.args.get('id')
    name = str(request.args.get('name'))
    location = str(request.args.get('location'))
    photo = str(request.args.get('photo'))
    types = str(request.args.get('type'))
    if ids is None:
        return flash('Error there is not place to be deleted', 'error')

    saved = Places.query.filter_by(ids=ids, name=name, location=location, photo=photo, types=types).one()
    if saved is None:
        flash('Cannot Delete Possibly Already Deleted', 'error')
        return render_template('Dashboard.html')

    db.session.delete(saved)
    db.session.commit()

    flash('Successfully Deleted from Dashboard')
    return render_template('Dashboard.html')


@app.route('/deleteAll')
@login_required
def deleteAll():
    Places.query.delete()
    db.session.commit()
    return render_template('/Dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
