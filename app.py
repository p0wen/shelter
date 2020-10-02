import os
from flask import Flask
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask('__name__')

app.config.from_object("env")

@app.route('/')
def welcome():
    return 'Welcome Stranger - Lets do this!'


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
