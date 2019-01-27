from datetime import datetime
from flask import Flask, session, request, flash, url_for, redirect, render_template, abort , g
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import googlemaps, requests, json, time
from googlemaps.places import places_autocomplete_session_token
import sqlalchemy, sqlalchemy_utils
#from googleplaces import GooglePlaces, types, lang

key = 'AIzaSyAoMCCon3EqNo4HUCaDsCVegwG4P5sTxkE'

error_type = ''
error = ''

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://id8571093_yas19sin:yobama@atabases.000webhost.com/id8571093_maindb'
#engine = create_engine('mysql://id8571093_yas19sin:yobama@atabases.000webhost.com/id8571093_maindb')
wsgi_app = app.wsgi_app
db = SQLAlchemy(app)
google_places = googlemaps.Client(key)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#def get_users_location():
    #URL = ('https://api.ipgeolocation.io/ipgeo?apiKey=dbe5400141564b12ad9e379e679fb327')
    #r = requests.get(URL)
    #respone = r.text
    #locations = json.loads(respone)
    #lat = locations['latitude']
    #long = locations['longitude']
    #return long + ',' + lat


"""def get_nearby_places(coordinates, business_type, next_page):
    global testing
    URL = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='
		+get_users_location()+'&radius=10000'+ '&types='+ business_type
        +'&key=' + key)
    print(get_users_location())
    r = requests.get(URL)
    response = r.text
    print(r.status_code)
    print(r.text)
    python_object = json.loads(response)
    error_type= python_object["status"]
    if(error_type == 'ZERO_RESULTS'):
        error = '0 Results - No Results'
        return error
    if(error_type == 'OK'):
        error = 'no error ok status'
        return error
    if(error_type == 'OVER_QUERY_LIMIT'):
        error = 'error too much requests'
        return error
    results = python_object["results"]
    testit = python_object["results"]
    for result in results:
        if "name" in result:
            place_name = result["name"]
        else:
            place_name = "no name"
        place_id = result["place_id"]
        if "icon" in result:
            place_img = result["icon"]
        else:
            place_img = "no image"
        if "vicinity" in result:
            place_location = result["vicinity"]
        else:
            place_location = "no location"
        if "types" in result:
            place_type = result["types"]
        else:
            place_type = "no type found"
        website = get_place_website(place_id)
        print([business_type, place_name, website])
        total_results.append([business_type, place_name, website])
    try:
        next_page_token = python_object["next_page_token"]
    except KeyError:
        return
    time.sleep(1)
    testing = [{'name': place_name, 'photo': place_img, 'type': place_type,'location': place_location, 'website': website}]
    testing = [{'name': 'Mabrouk', 'photo': "picture.png", 'type': 'Food place', 'location': 'Morocco, Sale, Sidi Moussa', 'rating': '3'}]
    get_nearby_places(cooredinates, business_type, next_page_token)
"""

def get_place_website(place_id):
    reqURL = ('https://maps.googleapis.com/maps/api/place/details/json?placeid='
              +place_id+'&key='+key)
    r = requests.get(reqURL)
    response = r.text
    python_object = json.loads(response)
    try:
        place_details = python_object["result"]
        if 'website' in place_details:
            return place_details['website']
        else:
            return "no website listed in API"
    except:
        print("err getting place details")

@app.route('/Search', methods=['POST', 'GET'])
@login_required
def Search():
    testing = ['']
    total_results = ['']
    jreq = ('https://api.ipgeolocation.io/ipgeo?apiKey=dbe5400141564b12ad9e379e679fb327')
    rq = requests.get(jreq)
    res = rq.text
    print(rq.status_code)
    print(rq.text)
    locations = json.loads(res)
    lat = locations['latitude']
    long = locations['longitude']
    print(lat)
    print(long)
    lat_loc = lat + ',' + long
    URL = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='
            +lat + ',' + long+'&radius=2000'+ '&types='+ 'store,stores'+ '&key=' + key)
    print(lat_loc)
    r = requests.get(URL)
    response = r.text
    print(r.status_code)
    print(r.text)
    python_object = json.loads(response)
    global error, error_type
    error_type= python_object["status"]
    if(error_type == 'ZERO_RESULTS'):
        error = '0 Results - No Results'
    if(error_type == 'OK'):
        error = 'no error ok status'
    if(error_type == 'OVER_QUERY_LIMIT'):
        error = 'error too much requests'
    print(error)
    results = python_object["results"]
    for result in results:
        if "name" in result:
            place_name = result["name"]
        else:
            place_name = "no name"
        place_id = result["place_id"]
        if "icon" in result:
            place_img = result["icon"]
        else:
            place_img = "no image"
        if "vicinity" in result:
            place_location = result["vicinity"]
        else:
            place_location = "no location"
        if "types" in result:
            place_type = result["types"]
        else:
            place_type = "no type found"
        time.sleep(2)
        website = get_place_website(place_id)
        print([place_name, place_img, place_type, place_location, website])
        total_results.append([place_name, place_img, place_type, place_location, website])
        testing = [{'name': place_name, 'photo': place_img, 'type': place_type,'location': place_location, 'website': website}]
        testing = [{'name': 'Mabrouk', 'photo': "picture.png", 'type': 'Food place', 'location': 'Morocco, Sale, Sidi Moussa', 'Website': 'https://unitedremote.com/developers'}]
        return render_template('Search.html', places = testing, error_is = error, all_places = total_results)
    testing = [{'name': 'Mabrouk', 'photo': "picture.png", 'type': 'Food place', 'location': 'Morocco, Sale, Sidi Moussa', 'Website': 'https://unitedremote.com/developers'}]
    return render_template('Search.html', places = testing, error_is = error, all_places = total_results)

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

db.create_all()
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

if __name__ == '__main__':
    app.secret_key = "unitedremote@2019"
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
