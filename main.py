from flask import Flask, request, render_template, flash, redirect, url_for
from flask_login import LoginManager, AnonymousUserMixin,login_required, login_user, logout_user, current_user
login_manager = LoginManager()
from aiocoap import *
import coapclient
from forms import LoginForm, RegisterForm, Create_EventForm
import sqlite3
from flask_bcrypt import Bcrypt
import secrets
from flask_socketio import SocketIO
import threading
import requests
import datetime
import os
login_manager.login_view = 'login'
secret_key = secrets.token_hex(16)
lamps_id = ['1a', '1b', '1c', '2a', '2b', '2c', '3a', '3b', '3c', '4a', '4b', '4c', '5a', '5b', '5c', 'Al']
app = Flask(__name__,template_folder='templates')
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
socketio = SocketIO(app, debug=True)
app.config['SECRET_KEY'] = secret_key
new_status = {'1a': 3, '1b':3, '1c':3, '2a': 3, '2b':3, '2c':3, '3a':3, '3b':3, '3c':3, '4a':3, '4b':3, '4c':3, '5a':3, '5b':3, '5c':3}    
status = {'1a': 30, '1b':30, '1c':30, '2a': 30, '2b':30, '2c':30, '3a':30, '3b':30, '3c':30, '4a':30, '4b':30, '4c':30, '5a':30, '5b':30, '5c':30}    
thread = None
thread_lock = threading.Lock()
async_mode = None
Base = ''

#class-user-------------------------------------------------------------------------------------------------------------------------------------------
class User(AnonymousUserMixin):
    def __init__(self, id,firstname, lastname, email, password, adm):
        self.id = id
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.adm = adm
    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return self.id
    def get_adm(self):
        print(self.adm)
        if self.adm == 1:
            return True
        else:
            return False

#Login-manager-------------------------------------------------------------------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT * from user where user_id = (?)",[user_id])
    lu = curs.fetchone()
    conn.close()
    print(lu)
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[2], lu[3], lu[4],int(lu[5]))

@socketio.on('disconnect')
def socketiodisconnected():
    print("Socketio disconnected.")

@socketio.on('connect')
def socketioconnected():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    socketio.emit('status', status, json=True, broadcast=True)
    print("Socketio session connected.", request.sid)

@socketio.on('change')
def socketchanged():
    socketio.emit('status', new_status, json=True)

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else: return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    if current_user.get_adm():
        return render_template('admin.html')
    else: 
        return render_template('403.html')

@app.route('/log')
@login_required
def log():
    if current_user.get_adm():
        try:
            conn = sqlite3.connect('database.db')
            curs = conn.cursor()
            curs.execute("SELECT user.first_name, user.last_name, log.time, log.a1, log.b1, log.c1, log.a2, log.b2, log.c2, log.a3, log.b3, log.c3, log.a4, log.b4, log.c4, log.a5, log.b5, log.c5, user.user_id FROM user INNER JOIN log ON user.user_id = log.user_id")
            data = curs.fetchall()
            conn.close()
        except Exception as e:
            print("Failed to fetch data from database")
            print(e)
            data = None
        return render_template('log.html', data=data)
    else: 
        return render_template('403.html')

@app.route('/home')
@login_required
def home():
    if current_user.get_adm():
        return redirect(url_for("admin"))
    else:
        return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return redirect(url_for('login'))

@app.route('/set/<lamp_id>', methods=["Get","POST"])
async def set(lamp_id):
    print(lamp_id)
    data = request.form
    try:
        if lamp_id == 'Al':
            for id in lamps_id[:-1]:
                new_status[id] = data["dimming"] 
                try:
                    await coapclient.coapsetlampstatus('coap://lamp' + id + '.irst.be/lamp/dimming', bytes(data["dimming"].encode()), lamp_id, data)
                except:
                    print('network error')
        else:
            new_status[lamp_id] = data["dimming"] 
            try:
                await coapclient.coapsetlampstatus('coap://lamp' + lamp_id + '.irst.be/lamp/dimming', bytes(data["dimming"].encode()), lamp_id, data)
            except:
                print('network error')
        log_changes()
        socketio.emit('status', status, json=True, broadcast=True)
        return '200'
    except:
        return '404'

#App-route-login----------------------------------------------------------------------------------------------------------------------------
@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            print(form.email.data)
            conn = sqlite3.connect('database.db')
            curs = conn.cursor()
            curs.execute("SELECT * FROM user where email = (?)",[form.email.data])
            user = curs.fetchone()
            Us = load_user(user[0])
            print(Us)
            conn.close()
            if form.email.data == Us.email and bcrypt.check_password_hash(Us.password, form.password.data):
                login_user(Us, remember=form.remember.data)
                print('test')
                return redirect(request.args.get("next") or url_for("home"))
            else:
                flash('Password or email wrong.')
                return render_template('login.html',title='Login', form=form)
        except:
                flash('You don not have an acount.')
                return render_template('login.html',title='Login', form=form)
    else:
        return render_template('login.html',title='Login', form=form)

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            conn = sqlite3.connect('database.db')
            curs = conn.cursor()
            print(form.email.data)
            try:
                curs.execute("SELECT * FROM user where email = (?)",[form.email.data])
                user = curs.fetchone()
                if user == None:
                    curs.execute("INSERT INTO user (first_name, last_name, email, password, admin) values (?,?,?,?,?)",(form.first.data, form.last.data, form.email.data, bcrypt.generate_password_hash(form.password.data), '0'))
                    conn.commit()
                    conn.close()
                    flash("registration succesfull")
                    print('no user found')
                    return redirect(url_for('index'))
                else:
                    flash('E-mail is already registerd')
            except Exception as e:
                flash("Could not enter to database")
                print(e)
        except:
            flash("Registration failed")
    return render_template('register.html',title='register', form=form)

def emit_update():
    global status
    test = requests.get('http://127.0.0.1:8080/getAll')
    print(test.json())
    status = test.json()
    socketio.emit('status', status, json=True, broadcast=True)
    #new_status = status
    #socketio.emit('status', new_status, json=True, broadcast=True)

def background_thread():
    while True:
        socketio.sleep(1)
        emit_update()

def log_changes():
    print('logging changes')
    try:
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("INSERT INTO log (user_id, time, a1, b1, c1, a2, b2, c2, a3, b3, c3, a4, b4, c4, a5, b5, c5) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(current_user.get_id(), datetime.datetime.now(), int(status['1a']), int(status['1b']), int(status['1c']), int(status['2a']), int(status['2b']), int(status['2c']), int(status['3a']), int(status['3b']), int(status['3c']), int(status['4a']), int(status['4b']), int(status['4c']), int(status['5a']), int(status['5b']), int(status['5c'])))
        conn.commit()
        conn.close()
    except Exception as err:
        print('failed to save changes to database')
        print(err)

if __name__ == "__main__":
    with threading.Lock():
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        Base = request.base_url
        emit_update()
        os.system("create_database.py")
        os.system("subServer.py")
        print(Base)