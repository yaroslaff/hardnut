import os
import json

from flask import Blueprint, request, abort, send_file, Response, make_response
from flask_login import login_required, current_user

from user import User, UserNotFound, UserHomeRootViolation, UserHomePermissionViolation
from app import App


var_bp = Blueprint('var', __name__)


def set_flags(path):
    if not current_user.is_authenticated:
        abort(401)

    with open(path, "r") as fh:
        data = json.load(fh)
        if 'set_flags' not in data['control']['user_actions']:
            abort(403, f'This action not allowed for {path}')

        for flag in request.json:
            print("set flag", flag)

    return Response('Set_flags worked')

#### POST ####
@var_bp.route('/', defaults={'path': ''}, methods=['POST'])
@var_bp.route('/<path:path>', methods=['POST'])
def post(path):

    actions = {
        'set_flags': set_flags
    }

    if not request.json or 'action' not in request.json:
        return Response('Incorrect JSON request', status=400)

    app = App()

    if '..' in path:
        abort(404)

    try:
        filepath = app.localpath('var/'+path)
        print(path, filepath)
        if os.path.isfile(filepath):
            action = actions.get(request.json['action'], lambda: "Incorrect action")
            return action(filepath)    
        else:
            abort(404)
    except (UserHomeRootViolation, UserHomePermissionViolation) as e:
        print(f'{type(e)} exception: {e}')
        abort(403)



    app = App()

    # Either user authenticated or API-KEY
    if 'X-API-KEY' in request.headers:
        print("API KEY")
    app.check_key()
    
    
    if '..' in path:
        abort(404)

    # security checks
    # if request.method in ['PUT', 'DELETE']
    try:
        filepath = app.localpath('var/'+path)
        print(path, filepath)
        if os.path.isfile(filepath):
            return 'ZZZ'
        else:
            abort(404)
    except (UserHomeRootViolation, UserHomePermissionViolation) as e:
        print(f'{type(e)} exception: {e}')
        abort(403)
