import json
import pandas as pd
import sqlite3
import pickle
from functools import wraps
from time import time
from flask import Flask, request, g, app, jsonify
from flask_restplus import Resource, Api, abort, fields, inputs, reqparse
from itsdangerous import SignatureExpired, JSONWebSignatureSerializer, BadSignature
from flask_cors import CORS
import flask_monitoringdashboard as dashboard

# would require to implement a database for the analytics API as well as users login
DATABASE = './cars.db'

# ---------------ML loading model and encoder
#f = open('Server/ml_model/encoder', 'rb')
f = open('./ml_model/encoder', 'rb')
enc = pickle.loads(f.read())

#f = open('Server/ml_model/model', 'rb')
f = open('./ml_model/model', 'rb')
regressor = pickle.loads(f.read())


# ----------------Database function
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# ------------------Token Functions
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


# ----------------------app set up procedure
SECRET_KEY = "A SECRET KEY; USUALLY A VERY LONG RANDOM STRING"
expires_in = 6000
auth = AuthenticationToken(SECRET_KEY, expires_in)

app = Flask(__name__)
dashboard.bind(app)

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

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# ----------------------authentication accesses for end point
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')

        try:
            user = auth.validate_token(token)
            print(user);
        except SignatureExpired as e:
            abort(401, e.message)
        except BadSignature as e:
            abort(401, e.message)

        return f(*args, **kwargs)

    return decorated

# might delete if we can't do for flask monitoring dashboard, then use config.cfg as config and edit there
def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')
        try:
            user = auth.validate_token(token)
            checkadmin = query_db('select username from Admins where username = ?', [user], one=True);
            if user not in checkadmin:
                abort(403, 'Access Forbidden Error')
            print(user)
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
username_parser = reqparse.RequestParser()
username_parser.add_argument('username', type=str)


# --------------------------API end points
@api.route('/user')
class User(Resource):
    @api.response(200, 'user details get')
    @api.doc(description='retrieve username and password')
    @api.expect(username_parser, validate=True)
    def get(self):
        users = query_db('select user_id, username from Users ')
        users = jsonify(users)
        return users

    @api.response(201, 'user created')
    @api.doc(description='creating a user')
    @api.expect(credential_parser, validate=True)
    def post(self):
        args = credential_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        if (query_db('select * from Users where username = ?', [username], one=True) != None):
            return {"Error": "User already exist!"}, 400
        db = query_db('insert into Users (username, password) values (?,?)', [username, password])
        db = query_db('select * from Users where username = ?', [username], one=True)
        print(db)
        Base = get_db()
        Base.commit()
        return {"message": "User created!"}

    @api.response(200, 'User Grant Admin Access')
    @api.doc(description='gives a user admin status')
    @api.expect(username_parser, validate=True)
    def put(self):
        args = username_parser.parse_args()
        username = args.get('username')
        if (query_db('select * from Users where username = ?', [username], one=True) != None):
            return {"Error": "User doesn't exist!"}, 400
        else:
            db = query_db('insert into Users (username) values (?)', [username], one=True)
            Base = get_db()
            Base.commit()
        # ----------------------------------------raise user to admin here
        return {'message': 'Access granted'}

    @api.response(200, 'User deleted')
    @api.doc(description='deletes a user register from records')
    @api.expect(username_parser, validate=True)
    @requires_auth
    def delete(self):
        args = username_parser.parse_args()
        username = args.get('username')
        if query_db('select * from Users where username = ?', [username], one=True) is None:
            return {"Error": "User does not exist!"}, 400
        else:
            query_db('delete from Users where username = ?',[username], one=True)
            if query_db('select * from Admins where username = ?', [username], one=True) is not None:
                query_db('delete from Admins where username = ?',[username], one=True)
            Base = get_db()
            Base.commit()
        # ----------------------------------------------------------------------delete user here
        return {'message': 'user has been deleted'}


@api.route('/user/<int:user_id>')
class FindUser(Resource):
    @api.response(200, 'User successfully return')
    @api.doc(description='returns a username according to their id')
    def get(self, user_id):
        userinfo = query_db('select user_id, username from Users where user_id = ?',[user_id], one=True)
        userinfo = jsonify(userinfo)
        return userinfo

@api.route('/session')
class Session(Resource):
    @api.response(200, 'successfully get current session')
    @api.doc(description='gets the current user login')
    def get(self):
        token = request.headers.get('AUTH-TOKEN')
        # due to programming  by contract, the session should be validated by @require_auth and always have a valid
        # session
        user = auth.validate_token(token)
        return {'username': user}

    @api.response(201, 'Session created Successfully')
    @api.doc(description="Generates a authentication token for the user session")
    @api.expect(credential_parser, validate=True)
    def post(self):
        args = credential_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        # query database here, if username, then query if password is same  if nested if is true then return token
        checkuser = query_db('select password from Users where username = ?', [username], one=True);
        if checkuser is not None:
            if password == checkuser[0]:
                return {"token": auth.generate_token(username)}
        return {"message": "authorization has been refused for those credentials."}, 401


price_predict_parser = reqparse.RequestParser()
price_predict_parser.add_argument('brand', type=str)
price_predict_parser.add_argument('model', type=str)
price_predict_parser.add_argument('vehicleType', type=str)
price_predict_parser.add_argument('yearOfRegistration', type=str)
price_predict_parser.add_argument('gearbox', type=str)
price_predict_parser.add_argument('powerPS', type=int)
price_predict_parser.add_argument('kilometer', type=int)
price_predict_parser.add_argument('fuelType', type=str)
price_predict_parser.add_argument('notRepairedDamage', type=str)

# feature 1
@api.route('/estimatePrice')
class EstimatePrice(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Gives user a recommended price to sell the car")
    @api.expect(price_predict_parser, validate=True)
    def get(self):
        car = price_predict_parser.parse_args()
        df = [car.get('vehicleType'), car.get('yearOfRegistration'), car.get('gearbox'), car.get('model'),
              car.get('fuelType'), car.get('brand'), car.get('notRepairedDamage')]
       # print(df)
        powerPS = car.get('powerPS')
        kilometer = car.get('kilometer')
        x = enc.transform([df])
        X = []
        X.append(x.toarray()[0].tolist())
        X = X[0] + [powerPS] + [kilometer]
        y_pred = regressor.predict([X])
        return {"Predicted_Price": y_pred[0]}, 200

# feature 2
@api.route('/estimateCar/<int:budget>/<brand>')
class EstimateCar(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Gives user a recommended car [list] for a given budget")
    # def get(self,budget):
    #     rec = df['price'].isin(range(budget-200,budget+200))
    #     df_rec = df.loc[rec,['model','brand','price']]
    #     df_rec.reset_index(drop=True, inplace=True)
    #     json_str=df_rec.to_json(orient='split')
    #     ds = json.loads(json_str)
    #     return ds

    def get(self, budget, brand):
        rec = df['price'].isin(range(budget - 50, budget + 50))
        df_rec = df.loc[rec, ['model', 'brand', 'yearOfRegistration']]
        df_rec = df_rec.loc[df_rec['model'] != 'other']
        df_rec = df_rec.loc[df_rec['brand'] == brand]
        df_rec = df_rec[['model', 'brand', 'yearOfRegistration']].drop_duplicates()
        json_str = df_rec.to_json(orient='records')
        ds = json.loads(json_str)
        return ds


# feature 3
@api.route('/reliability')
class Reliability(Resource):
    @api.response(200, 'Successful')
    @api.doc(desciption='')
    def get(self):
        return{'message':'return a brand'}

@api.route('/usageStats')
class ApiUsage(Resource):
    @api.response(200, 'Successful')
    @requires_admin
    @api.doc(description="API usage statistics")
    def get(self):
        db = query_db('select * from apiusage')
        packet = jsonify(db)
        return packet;


if __name__ == '__main__':
    # preprocessing done in data_preprocessing directory, and the final csv after preprocessing is preprocessed.csv
    # df = pd.read_csv("Server/data_preprocessing/preprocessed.csv")
    df = pd.read_csv("./data_preprocessing/preprocessed.csv")
    df['price'] = df['price'].astype('int')
    #  df.set_index('name',inplace=True)
    app.run(port=9000, debug=True);  # debug to be turned off  when deployed
