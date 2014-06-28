import json
import urllib2

from flask import Flask
from flask import request
from flask import render_template
from flask import session
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

#PACKAGE APIPM#
from .helper import *
from .views import *

# facebook
APPTOKEN = '401068586702319|5f78073b1129c9ff17880a96b6bf9ac9'
APPID = '401068586702319'

# LOG FILE
handler = RotatingFileHandler('apipm.log', maxBytes=10000, backupCount=1)
formatter = logging.Formatter("[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s")
handler.setFormatter(formatter)

#LOG EMAIL
ADMINS = ['lucarin91@gmail.com']
mail_handler = SMTPHandler('127.0.0.1',
                           'gitlab@sfcoding.com',
                           ADMINS, 'YourApplication Failed')
mail_handler.setLevel(logging.ERROR)


app = Flask(__name__)
app.config.from_envvar('WSGI_ENV')
app.secret_key = 'asdasdasd'
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(mail_handler)

#sql = application.config['SQL']
#Database.sql = sql
where = app.config['WHERE']


def requiresLogin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'idFacebook' not in session:
            return 'session error'
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requiresLogin
def index():
    return 'ciao ' + where + ss

eventoView = requiresLogin(Event.as_view('event'))
attributoView = requiresLogin(Attributi.as_view('attr'))
risposteView = requiresLogin(Risposte.as_view('ris'))
userView = requiresLogin(User.as_view('user'))
friendsView = requiresLogin(Friends.as_view('friends'))

# EVENTO
app.add_url_rule('/event', view_func=eventoView, methods=['GET', 'POST'])
app.add_url_rule('/event/<int:idEvento>', view_func=eventoView, methods=['DELETE', ])

# ATTRIBUTI
app.add_url_rule('/event/<int:idEvento>', view_func=attributoView, methods=['GET', 'POST'])
app.add_url_rule('/event/<int:idEvento>/<int:idAttributo>',
                 view_func=attributoView, methods=['DELETE', ])

# RISPOSTE
app.add_url_rule('/event/<int:idEvento>/<int:idAttributo>',
                 view_func=risposteView, methods=['GET', 'POST'])
app.add_url_rule('/event/<int:idEvento>/<int:idAttributo>/<int:idRisposta>',
                 view_func=risposteView, methods=['PUT', 'DELETE'])

# USER
app.add_url_rule('/user', view_func=userView, methods=['POST', ])

# FRIENDS
app.add_url_rule('/friends/<int:idEvento>', view_func=friendsView, methods=['GET', 'POST'])
app.add_url_rule('/friends/<int:idEvento>/<idFacebook>',
                 view_func=friendsView, methods=['DELETE', ])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['idFacebook'] != '' and request.form['token'] != '':
        token = request.form['token'].strip()
        idFacebook = request.form['idFacebook'].strip()

        try:
            data = json.load(urllib2.urlopen(
                'https://graph.facebook.com/debug_token?input_token=' + token + '&access_token=' + APPTOKEN))['data']

            if (data['is_valid'] == True and data['app_id'] == APPID and data['user_id'] == idFacebook):
                session['idFacebook'] = data['user_id']
                return 'fatto'
            else:
                return 'login fallito'
        except Exception, e:
            return 'login error ' + str(e)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('idFacebook', None)
    return 'fatto'

'''
DEBUG FUNCTION
'''


@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST' and request.form['idFacebook'] != '':
        idFacebook = request.form['idFacebook']
        sendNotification(idFacebook, {'type': CODE.t['test']})
        return 'fatto'
    else:
        return render_template('send.html')


@app.route("/lista", methods=['GET', 'POST'])
def lista():
    if request.method == 'POST':
        table = request.form['table']
        try:
            cur = sql.cursor()
            if table == 'utenti':
                cur.execute("SELECT * FROM utenti")
            elif table == 'evento':
                cur.execute("SELECT * FROM evento")
            elif table == 'party':
                cur.execute("SELECT * FROM party")
            elif table == 'attributi':
                cur.execute("SELECT * FROM attributi")
            elif table == 'risposte':
                cur.execute("SELECT * FROM risposte")
            elif table == 'rispose':
                cur.execute("SELECT * FROM rispose")
            else:
                return 'parametro non riconosciuto'

            ris = cur.fetchall()
            return str(ris)

        except Exception, e:
            sql.rollback()
            return 'error ' + str(e)
        finally:
            cur.close()
    else:
        return render_template('list.html')
