import json
import io
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
import sqlite3
import pickle
from functools import wraps
from time import time
from flask import Flask, request, g, app, jsonify, send_file
from flask_restplus import Resource, Api, abort, fields, inputs, reqparse
from itsdangerous import SignatureExpired, JSONWebSignatureSerializer, BadSignature
from flask_cors import CORS
import flask_monitoringdashboard as dashboard
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

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
    @requires_auth
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
    @requires_admin
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
    @requires_admin
    def delete(self):
        args = username_parser.parse_args()
        username = args.get('username')
        if query_db('select * from Users where username = ?', [username], one=True) is None:
            return {"Error": "User does not exist!"}, 400
        else:
            query_db('delete from Users where username = ?', [username], one=True)
            if query_db('select * from Admins where username = ?', [username], one=True) is not None:
                query_db('delete from Admins where username = ?', [username], one=True)
            Base = get_db()
            Base.commit()
        # ----------------------------------------------------------------------delete user here
        return {'message': 'user has been deleted'}


@api.route('/user/<int:user_id>')
class FindUser(Resource):
    @api.response(200, 'User successfully return')
    @api.doc(description='returns a username according to their id')
    def get(self, user_id):
        userinfo = query_db('select user_id, username from Users where user_id = ?', [user_id], one=True)
        userinfo = jsonify(userinfo)
        return userinfo


@api.route('/session')
class Session(Resource):
    @api.response(200, 'successfully get current session')
    @api.doc(description='gets the current user login')
    def get(self):
        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')
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
@api.route('/price')
class Price(Resource):
    @api.response(200, 'Success')
    @api.doc(description="Gives user a recommended price to sell the car")
    @api.expect(price_predict_parser, validate=True)
    @requires_auth
    def get(self):
        car = price_predict_parser.parse_args()
        df = [car.get('vehicleType'), car.get('gearbox'), car.get('model'),
              car.get('fuelType'), car.get('brand'), car.get('notRepairedDamage')]
        powerPS = car.get('powerPS')
        kilometer = car.get('kilometer')
        yearOfRegistration = car.get('yearOfRegistration')
        x = enc.transform([df])
        X = []
        X.append(x.toarray()[0].tolist())
        X = X[0] + [yearOfRegistration] + [powerPS] + [kilometer]
        y_pred = regressor.predict([X])
        return {"Predicted_Price": y_pred[0]}, 200


# feature 2
@api.route('/cars/<int:budget>/<brand>')
class Cars(Resource):
    @api.response(200, 'Success')
    @api.doc(description="Gives user a recommended car [list] for a given budget")
    @requires_auth
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
    @api.response(200, 'Success')
    @api.doc(description='Returns the top 10 most reliable car brands with their reliability indices')
    @requires_auth
    def get(self):
        rel_df = df[['brand','Reliability Index']]
        
        rel_df = rel_df[['brand', 'Reliability Index']].drop_duplicates()     
        rel_df = rel_df.nsmallest(30,'Reliability Index')
        rel_df.reset_index(inplace=True)
        rel_df['colors'] = ['red' if x >100 else 'green' for x in rel_df['Reliability Index']]
        rel_df.rename(columns={"Reliability Index": "reliability"})
        rel_df.rename(columns={'Reliability Index':'reliability'}, inplace=True)
        matplotlib.use('Agg')
        plt.figure(figsize=(14,10), dpi= 80)
        plt.hlines(y=rel_df.brand, xmin=0, xmax=rel_df.reliability, color=rel_df.colors, alpha=0.4, linewidth=5)
        for x, y, tex in zip(rel_df.reliability, rel_df.brand, rel_df.reliability):

            t = plt.text(x, y, round(tex, 2), horizontalalignment='left', 
                 verticalalignment='center', fontdict={'color':'red' if x >100 else 'green', 'size':14})
        plt.gca().set(ylabel='$Brand$', xlabel='$Reliability Index$')
        plt.title('Brandwise Reliability Index', fontdict={'size':20})
        plt.grid(linestyle='--', alpha=0.5)
        plt.savefig('reliability.png')  
        filename = 'reliability.png'

        return send_file(filename, mimetype='image/png')

        


# feature 4
reliability_avgprice_parser = reqparse.RequestParser()
reliability_avgprice_parser.add_argument('Brand_1', type=str)
reliability_avgprice_parser.add_argument('Brand_2', type=str)

@api.route('/graphcomparisons')
class Graphcomparisons(Resource):
    @api.response(200, 'Success')
    @api.doc(description='Compares 2 brands on reliability index and average repair cost and generates a graph')
    @api.expect(reliability_avgprice_parser, validate=True)
    @requires_auth
    def get(self):
        car = reliability_avgprice_parser.parse_args()
        user_brand_1 = car.get('Brand_1')
        user_brand_2 = car.get('Brand_2')
        rel_df = df[['brand', 'Reliability Index', 'Average Repair Cost']]
        rel_df = rel_df[['brand', 'Reliability Index', 'Average Repair Cost']].drop_duplicates()
        data_brand_1 = rel_df.loc[rel_df['brand'] == user_brand_1]
        data_brand_2 = rel_df.loc[rel_df['brand'] == user_brand_2]
        reli_brand_1 = int(data_brand_1["Reliability Index"])
        reli_brand_2 = int(data_brand_2["Reliability Index"])
        avg_repair_brand_1 = float(data_brand_1["Average Repair Cost"])
        avg_repair_brand_2 = float(data_brand_2["Average Repair Cost"])

        reliability = [reli_brand_1, reli_brand_2]
        repair = [avg_repair_brand_1, avg_repair_brand_2]
        index = [user_brand_1, user_brand_2]
        rel_df = pd.DataFrame({'Reliability': reliability,'Average Repair Cost': repair}, index=index)
        ax = rel_df.plot.bar(rot=0, color=['lightpink', 'skyblue'])
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True)
        plt.xlabel('Brand')
        plt.savefig('reliability_compare.png')  
        filename = 'reliability_compare.png'
        return send_file(filename, mimetype='image/png')


@api.route('/comparisons')
class Comparisons(Resource):
    @api.response(200, 'Success')
    @api.doc(description='Compares 2 brands on their reliability index and average repair cost')
    @api.expect(reliability_avgprice_parser, validate=True)
    @requires_auth
    def get(self):
        car = reliability_avgprice_parser.parse_args()
        user_brand_1 = car.get('Brand_1')
        user_brand_2 = car.get('Brand_2')
        rel_df = df[['brand', 'Reliability Index', 'Average Repair Cost']]
        rel_df = rel_df[['brand', 'Reliability Index', 'Average Repair Cost']].drop_duplicates()
        data_brand_1 = rel_df.loc[rel_df['brand'] == user_brand_1]
        data_brand_2 = rel_df.loc[rel_df['brand'] == user_brand_2]
        reli_brand_1 = int(data_brand_1["Reliability Index"])
        reli_brand_2 = int(data_brand_2["Reliability Index"])
        avg_repair_brand_1 = float(data_brand_1["Average Repair Cost"])
        avg_repair_brand_2 = float(data_brand_2["Average Repair Cost"])
        message = {
            'Brand_1_reliability': reli_brand_1,
            'Brand_1_avgcost': avg_repair_brand_1,
            'Brand_2_reliability': reli_brand_2,
            'Brand_2_avgcost': avg_repair_brand_2
        }
        message = jsonify(message) 
        return message



loan_parser = reqparse.RequestParser()
loan_parser.add_argument('principal', type=int)
loan_parser.add_argument('term', type=int)
loan_parser.add_argument('interest', type=float)

#feature 5
@api.route('/loans')
class Loan(Resource):
    @api.response(200, 'Success')
    @api.expect(loan_parser, validate=True)
    @api.doc(description='Gives user the amount he needs to pay every month for loan payment')
    @requires_auth
    def get(self):
        args = loan_parser.parse_args()
        interest = args.get('interest')
        budget = args.get('principal')
        term = args.get('term')
        interest = interest / 100
        amount = (budget * (interest / 12)) / (1 - (1 + interest/12) ** -term)
        print(interest, budget, term)
        return amount


if __name__ == '__main__':
    # preprocessing done in data_preprocessing directory, and the final csv after preprocessing is preprocessed.csv
    #df = pd.read_csv("Server/data_preprocessing/preprocessed.csv")
    df = pd.read_csv("./data_preprocessing/preprocessed.csv")
    df['price'] = df['price'].astype('int')
    #  df.set_index('name',inplace=True)
    app.run(port=9000, debug=True);  # debug to be turned off  when deployed
