# encoding: utf-8

from flask import Blueprint, request, jsonify, session, current_app

import ckan.plugins.toolkit as toolkit
from ckan.views.user import set_repoze_user
from ckan.common import config, g, request
import ckan.model as model

import requests
import jwt, logging
from helper import Helper
from datetime import datetime
import json

log = logging.getLogger(__name__)

ssoauth = Blueprint(u'open-login', __name__)

def index():
    return 'hello'

def getAccessToken(shortToken):
    helper = Helper()
    # betimes
    # base_url = "https://mmsuat.demotoday.net/login/api/Login/GetToken/"
    # uat sso
    base_url = "https://mmsuat.sso.go.th/login/api/Login/GetToken/"
    endpoint = base_url + str(shortToken)

    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            access_token = response.json().get("accessToken")
            userData = decode_jwt_to_json(access_token)

            userName = userData["preferred_username"]
            firstName = userData["given_name"]
            lastName = userData["family_name"]
            email = userData["email"]

            user = helper.identify(email, userName, firstName, lastName)
            if not user:
                helper.create_user(email, userName, firstName, lastName)
                
            userValid = helper.get_user(userName)
            data_dict = json.loads(userValid)
            test = data_dict["name"]

            session['name'] = data_dict['name']
            session['fullname'] = data_dict['fullname']
            session['email'] = data_dict['email']
            session['password'] = "12345678"

            g.userobj = model.User.by_name(session['name'])
            relay_state = request.form.get('RelayState')
            redirect_target = toolkit.url_for(
                str(relay_state), _external=True) if relay_state else u'user.me'

            resp = toolkit.redirect_to(redirect_target)
            set_repoze_user(session['name'], resp)
            return resp
        else:
            print("Failed to get access token.")
    except requests.exceptions.RequestException as e:
        pass

    # If something goes wrong, return an error response
    return jsonify({"error": "Failed to get access token."}), 500

def decode_jwt_to_json(jwt_token):
    try:
        decoded_payload = jwt.decode(jwt_token,
                                     verify=False)
        return decoded_payload
    except Exception as e:
        print(e)
    
    return None


ssoauth.add_url_rule('/open-login', view_func=index)
ssoauth.add_url_rule('/open-login/token/<shortToken>', view_func=getAccessToken, methods=['GET'])
