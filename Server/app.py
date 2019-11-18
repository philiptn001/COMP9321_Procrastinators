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

CORS(app, resources={r'/*': {'origins': '*'}})

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


def preprocessing():
    file = 'Server/autos.csv'
    df = pd.read_csv(file, encoding="latin-1")

    #dropping the columns that we don't need
    cols= [0, 1, 2, 3, 5, 16, 17, 18, 19]
    df = df.drop(df.columns[cols], axis=1)

    #changing NaN values to 'other' or 'unknown' based on context
    df["vehicleType"].fillna("other", inplace=True)
    df["model"].fillna("other", inplace=True)
    df["fuelType"].fillna("other", inplace=True)
    df["gearbox"].fillna("unknown", inplace=True)
    df["notRepairedDamage"].fillna("unknown", inplace=True)

    df = df[pd.notnull(df['price'])]
    df = df[df.vehicleType != 'volkswagen']

    #Removing invalid vehicle registration years
    df = df[(df["yearOfRegistration"] >= 1950) & (df["yearOfRegistration"] <= 2019)]
    df["monthOfRegistration"].replace([0, 12], [1, 11], inplace=True)


    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    df["monthOfRegistration"].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], months, inplace=True)

    median = df.groupby("vehicleType")["price"].median()

    # 75th percentile of the prices of all the vehicles types
    quantile75 = df.groupby("vehicleType")["price"].quantile(0.75)

    # 25th percentile of the prices of all the vehicles types
    quantile25 = df.groupby("vehicleType")["price"].quantile(0.25)

    # Calculating the value of the prices of each vehicle type above which all the values are outliers
    iqr = (quantile75 - quantile25) * 1.5 + median



    # Removing the outliers as per the logic above
    df = df[((df["vehicleType"] == "small car") & (df["price"] <= iqr['small car'])) |
            ((df["vehicleType"] == "other") & (df["price"] <= iqr['other'])) |
            ((df["vehicleType"] == "suv") & (df["price"] <= iqr['suv'])) |
            ((df["vehicleType"] == "station wagon") & (df["price"] <= iqr['station wagon'])) |
            ((df["vehicleType"] == "bus") & (df["price"] <= iqr['bus'])) |
            ((df["vehicleType"] == "cabrio") & (df["price"] <= iqr['cabrio'])) |
            ((df["vehicleType"] == "limousine") & (df["price"] <= iqr['limousine'])) |
            ((df["vehicleType"] == "coupe") & (df["price"] <= iqr['coupe'])) ]


    #fixing columns with mixed types
    df["kilometer"] = pd.to_numeric(df["kilometer"])


    # Reading the second csv
    df_rel = pd.read_csv('Server/car_reliability.csv')

    df_rel = df_rel.drop(df_rel.columns[3:], axis=1)
    df_rel = df_rel.drop(df_rel.columns[0], axis=1)

    # Reading the third csv

    df_avgcost = pd.read_csv('Server/avgrepaircost.csv')
    df_avgcost = df_avgcost.drop(df_avgcost.columns[0], axis=1)


    join_df = pd.merge(df_avgcost, df_rel, how='left', left_on=['Make and Model'], right_on=['Make and Model'])


    df['brand'] = df['brand'].str.capitalize()

    df['brand'] = df['brand'].apply(lambda x: 'Mercedes-Benz' if 'Mercedes_benz' in x else x.replace('_', ' '))
    df['brand'] = df['brand'].apply(lambda x: x.upper() if 'Bmw' in x else x)
    df['brand'] = df['brand'].apply(lambda x: x.upper().replace(' ','') if 'Land rover' in x else x)

    main_df = pd.merge(df, join_df, how='left', left_on=['brand'], right_on=['Make and Model'])
    main_df = main_df.drop('Make and Model', axis=1)

    main_df = main_df.dropna()

    return main_df


if __name__ == '__main__':
    # preprocessing csv here
    df = preprocessing()
    print(df.head(10).to_string())
    app.run(port=9000, debug=True);  # debug to be turned off  when deployed
