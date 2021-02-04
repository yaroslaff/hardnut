import os
import json

from flask import Blueprint, request, abort, send_file, Response, make_response
from flask_login import login_required, current_user

from user import User, UserNotFound, UserHomeRootViolation, UserHomePermissionViolation
from app import App


home_bp = Blueprint('home', __name__)



#### GET ####
@login_required
def get(path):
    print("GET",path)
    current_user.app.check_origin()

    if '..' in path:
        abort(404)

    # security checks
    # if request.method in ['PUT', 'DELETE']
    try:
        filepath = current_user.localpath(path, 'r')
        if os.path.isfile(filepath):
            response = make_response(send_file(filepath))
            response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return(response)
        else:
            return current_user.app.cross_response(response='')
            print("404", filepath)
            abort(404)
    except (UserHomeRootViolation, UserHomePermissionViolation) as e:
        print(f'{type(e)} exception: {e}')
        abort(403)

get.provide_automatic_options = False
get.methods = ['GET']
home_bp.add_url_rule('/', 'get', get)
home_bp.add_url_rule('/<path:path>', 'get', get)

#### PUT ####
@login_required
def put(path):
    current_user.app.check_origin()
    try:
        filepath = current_user.localpath(path, 'w')
        with open(filepath, "wb") as fh:
            fh.write(request.get_data())
        response = Response(status=200, response=f'OK written {path}')
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return(response)
    except (UserHomeRootViolation, UserHomePermissionViolation) as e:
        print(f'{type(e)} exception: {e}')
        abort(403)

put.provide_automatic_options = False
put.methods = ['PUT']
home_bp.add_url_rule('/', 'put', put)
home_bp.add_url_rule('/<path:path>', 'put', put)

#### DELETE ####
@login_required
def delete(path):
    current_user.app.check_origin()
    try:
        filepath = current_user.localpath(path, 'w')
        if os.path.exists(filepath):
            os.unlink(filepath)
            response = Response(status=200, response=f'OK written {path}')
            response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return(response)
        else:
            abort(404)
            
    except (UserHomeRootViolation, UserHomePermissionViolation) as e:
        print(f'{type(e)} exception: {e}')
        abort(403)

delete.provide_automatic_options = False
delete.methods = ['DELETE']
home_bp.add_url_rule('/<path:path>', 'delete', delete)



#### OPTIONS ####

@home_bp.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@home_bp.route('/<path:path>', methods=['OPTIONS'])
# @login_required
def options(path):
    app = App()
    app.check_origin()
    response = app.cross_response(response='put')
    if path.startswith('rw/'):
        response.headers['Access-Control-Allow-Methods'] = 'GET, PUT'
    elif path.startswith('r/'):
        response.headers['Access-Control-Allow-Methods'] = 'GET'

    return response
