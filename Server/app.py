import json
import pandas as pd
import sqlite3
from functools import wraps
from time import time
from flask import Flask, request, g
from flask_restplus import Resource, Api, abort, fields, inputs, reqparse
from itsdangerous import SignatureExpired, JSONWebSignatureSerializer, BadSignature
from API.util import methods
from flask_cors import CORS

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# would require to implement a database for the analytics API as well as users login
DATABASE = './cars.db'


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in
        self.serializer = JSONWebSignatureSerializer(secret_key)

    def generate_token(self, username):
        info = {
            'username': username,
            'creation_time': time()
        }

        token = self.serializer.dumps(info)
        return token.decode()

    def validate_token(self, token):
        info = self.serializer.loads(token.encode())

        if time() - info['creation_time'] > self.expires_in:
            raise SignatureExpired("The Token has been expired; get a new token")

        return info['username']


SECRET_KEY = "A SECRET KEY; USUALLY A VERY LONG RANDOM STRING"
expires_in = 6000
auth = AuthenticationToken(SECRET_KEY, expires_in)

app = Flask(__name__)
api = Api(app, authorizations={
    'API-KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'AUTH-TOKEN'
    }
},
          security='API-KEY',
          default="Cars",  # Default namespace
          title="Cars Dataset",  # Documentation Title
          description="This is just a simple example to show how publish data as a service.")  # Documentation Description


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')

        try:
            user = auth.validate_token(token)
        except SignatureExpired as e:
            abort(401, e.message)
        except BadSignature as e:
            abort(401, e.message)

        return f(*args, **kwargs)

    return decorated


credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})

credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)


@api.route('/token')
class Token(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()

        username = args.get('username')
        password = args.get('password')

        if username == 'admin' and password == 'admin':
            return {"token": auth.generate_token(username)}

        return {"message": "authorization has been refused for those credentials."}, 401


@api.route('/estimatePrice')
class EstimatePrice(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Gives user a recommended price to sell the car")
    def get(self):
        return {"message": "hope you land a good deal"}


@api.route('/estimateCar')
class EstimateCar(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Gives user a recommended car [list] for a given budget")
    def get(self):
        return {"message": "to be implemented"}


@api.route('/signup')
class SignUp(Resource):
    @api.response(200, 'user created')
    @api.doc(description='creating a user')
    def post(self):
        return {"message": "User created!"}


@api.route('/usageStats')
class ApiUsage(Resource):
    @api.response(200, 'Successful')
    @requires_auth
    @api.doc(description="API usage statistics")
    def get(self):
        return {"message": "everything you need for JSCharts"}


if __name__ == '__main__':
    # preprocessing csv here
    app.run(port=9000, debug=True);  # debug to be turned off  when deployed
