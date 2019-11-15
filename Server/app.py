from flask import Flask
from flask_restplus import reqparse, abort, Api, Resource

app = Flask(__name__)
api=Api(app)

@app.route('/hello')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=9000, debug=True);#debug to be turned off  when deployed