import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask('__name__')

app.config.from_object('env')

mongo = PyMongo(app)


@app.route('/')
def welcome():
    return 'Welcome Stranger - Lets do this!'


@app.route('/get_gear')
def get_gear():
    return render_template("gallery.html", gear_collection=mongo.db.gear.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
