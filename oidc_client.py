from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from urllib.parse import urljoin

from flask import Blueprint, request, redirect, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


from app import App
from user import User, UserNotFound

oidc_bp = Blueprint('oidc', __name__)

@oidc_bp.route('/hello')
def hello():
    x = session.get('x', 0)
    session['x'] = x+1
    return f'Hello ({x})'

def get_provider_cfg(url):
    return requests.get(url).json()

@oidc_bp.route("/login/<provider>")
def login(provider):
    app = App(request.host)
    credentials = app.get_credentials(provider)
    client = WebApplicationClient(credentials['CLIENT_ID'])
    provider_cfg = get_provider_cfg(credentials['DISCOVERY_URL'])
    
    authorization_endpoint = provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=urljoin(request.url_root, "/oidc/callback"),
        scope=["openid", "email", "profile"],
    )
    session['oidc_provider'] = provider
    return redirect(request_uri)

@oidc_bp.route("/callback")
def callback():

    # Get authorization code Google sent back to you
    code = request.args.get("code")
    provider = session['oidc_provider']

    app = App(request.host)
    credentials = app.get_credentials(provider)
    client = WebApplicationClient(credentials['CLIENT_ID'])
    provider_cfg = get_provider_cfg(credentials['DISCOVERY_URL'])

    token_endpoint = provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            credentials['CLIENT_ID'], 
            credentials['CLIENT_SECRET'])
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userdata = userinfo_response.json()

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = f'{provider}:{userinfo_response.json()["sub"]}'
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return f"User email not available or not verified by {provider}.", 400

    # Create a user in your db with the information provided
    # by Google


    userinfo = {
        'id': unique_id,
        'name': users_name,
        'email': users_email,
        'profile_pic': picture
    }


    try:
        user = User.get(app, unique_id)
    except UserNotFound:
        print("no such user, create")

        user = User(
                id_ = unique_id, 
                app = app, 
                userinfo = userinfo
        )
        user.create()
    
    # Begin user session by logging the user in
    # print("login user", user)
    login_user(user)
    session['userinfo'] = userinfo
    session.permanent = True

    app_opts = app.get_config('etc/options.json')
    # print("return to:", app_opts['return_url'])
    return redirect(app_opts['return_url'])

    # Send user back to homepage
    # return redirect(url_for("index"))
