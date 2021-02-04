#!/usr/bin/env python3

# Python standard libraries
import json
import os
import argparse

# import sqlite3

# Third-party libraries
from flask import Flask, make_response, redirect, request, url_for, abort, Response, session
from flask_sessionstore import Session
# from requests.models import Response

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

# Internal imports
# from db import init_db_command
from config import config
from user import User, UserNotFound
from app import App

from oidc_client import oidc_bp
from home import home_bp
from app_api import api_bp
from var import var_bp

# Only for localhost testing
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Flask app setup
flask_app = Flask(__name__)
flask_app.register_blueprint(oidc_bp, url_prefix='/oidc')
flask_app.register_blueprint(home_bp, url_prefix='/~')
flask_app.register_blueprint(api_bp, url_prefix='/app')
flask_app.register_blueprint(var_bp, url_prefix='/var')


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(flask_app)

# flask_app.config['SESSION_TYPE'] = 'redis'

#print("CONFIG", flask_app.config)
#flask_app.config.from_object(Config)

#SESSION_TYPE = 'redis'
#flask_app.config.from_object(__name__)

#sess = Session()
#sess.init_app(flask_app)

flask_app.config.update(config)

Session(flask_app)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    app = App(request.host)
    # print("load user", app, user_id)
    try:
        return User.get(app, user_id)
    except UserNotFound:
        return None

# OAuth 2 client setup
# client = WebApplicationClient(GOOGLE_CLIENT_ID)

@flask_app.route("/")
def index():
    app = App(request.host)

    if current_user.is_authenticated:
        userinfo = session.get('userinfo', None)
        return (
            "<p>Hello, {}! You're ({}) logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                userinfo['name'], userinfo['id'], userinfo['email'], userinfo['profile_pic']
            )
        )
    else:        
        return f'<a class="button" href="{url_for("oidc.login", provider="Google")}">Google Login</a>'


@flask_app.route('/authenticated')
# @login_required
def authenticated():
    app = App(request.host)
    origin = request.headers['Origin']

    app.check_origin()

    if current_user.is_authenticated:
        response = Response('')
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    else:
        response = Response(status=401, response="Unauthorized")
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

@flask_app.route("/logout", methods=['POST'])
@login_required
def logout():
    app = App(request.host)
    app.check_origin()    
    logout_user()

    origin = request.headers['Origin']
    r = app.cross_response('Logged out')
    return r

def parse_args():
    def_secret = os.urandom(16)

    parser = argparse.ArgumentParser(description='HardNut Server')
    g = parser.add_argument('--secret', default=os.getenv('SECRET', def_secret), 
        help='secret key')
    g = parser.add_argument('--apps_path', default=os.getenv('APPS_PATH'), 
        help='path to apps directory')
    g = parser.add_argument_group('SSL certificate')
    g.add_argument('--cert', metavar='PATH', default=os.getenv('CERT'),
        help='path to certificate (fullchain.pem)')
    g.add_argument('--privkey', metavar='PATH', default=os.getenv('PRIVKEY'),
        help='path to certificate key (privkey.pem)')

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    App.apps_path = args.apps_path

    flask_app.secret_key = args.secret or os.urandom(24)

    # app.run(ssl_context="adhoc")
    flask_app.run(host='0.0.0.0', ssl_context = (args.cert, args.privkey))
            