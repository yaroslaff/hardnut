import os
import json
from os.path import abspath
import re

from flask import abort, request, Response

class App:

    apps_path = None
    provider_regex = re.compile('^[a-zA-Z0-9-_]+$')

    def __init__(self, url=None):

        url = url or request.host
        self.name = url.split('.')[0]
        self.root = os.path.join(self.apps_path, self.name)

        if not self.exist():
            abort(Response(f'App {app.name!r} not found', status=404))
        
        self.loaded_configs=dict()

    def exist(self):
        return os.path.isdir(self.root)

    def __repr__(self):
        return f'App {self.name!r}'
    
    def localpath(self, subpath):
        path = os.path.join(self.root, subpath)
        assert(os.path.abspath(path).startswith(self.root))
        return path

    def get_json_file(self, path):
        with open(self.localpath(path), "r") as fh:
            return json.load(fh)

    def get_credentials(self, provider):
        # sanitize name
        if not self.provider_regex.match(provider):
            abort(Response(status=400, response='Incorrect provider name'))

        # credentials = self.get_json_file('etc/oidc_credentials.json')
        credentials = self.get_config('etc/oidc_credentials.json')
        try:
            c = credentials[provider]
        except KeyError as e:
            abort(Response(status=404, response='No such provider'))
        return c

    def get_config(self, name):
        if name not in self.loaded_configs:
            self.loaded_configs[name] = self.get_json_file(name)
        return self.loaded_configs[name]
        
    def allowed_key(self, key):
        options = self.get_config('etc/options.json')
        if 'api-keys' not in options or not options['api-keys']:
            # no keys
            return True

        for ks in options['api-keys']:
            if ks['key'] == key:
                return True

    def check_key(self, key=None):
        key = key or request.headers.get('X-API-KEY','')
        if not self.allowed_key(key):
            abort(403, 'Incorrect X-API-KEY')

    def allowed_origin(self, origin):
        options = self.get_config('etc/options.json')
        return 'origins' in options and origin in options['origins']

    def check_origin(self, origin = None):
        origin = origin or request.headers['Origin']
        if not self.allowed_origin(origin):
            abort(403, 'Cross-Origin request not allowed from this origin')

    def cross_response(self, response=None, status=None):
        status = status or None
        origin = request.headers['Origin']
        headers = {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': 'true'
        }
        return Response(response=response, status=status, headers = headers)

