import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask('__name__')

app.config.from_object('env')

mongo = PyMongo(app)


@app.route('/')
def welcome():
    gear_collection = mongo.db.gear.find()
    return render_template("index.html", gear_collection = list(gear_collection))


@app.route('/get_gear')
def get_gear():
    return render_template("gallery.html", gear_collection=mongo.db.gear.find())

@app.route('/add_gear')
def add_gear():
    return render_template('add_gear.html',
                           categories=mongo.db.categories.find())

@app.route('/insert_gear', methods=['POST'])
def insert_gear():
    gear = mongo.db.gear
    gear.insert_one(request.form.to_dict())
    return redirect(url_for('get_gear'))

@app.route('/edit_gear/<gear_id>')
def edit_gear(gear_id):
    the_gear = mongo.db.gear.find_one({"_id": ObjectId(gear_id)})
    all_categories = mongo.db.categories.find()
    return render_template('edit_gear.html', gear=the_gear, categories=all_categories)


@app.route('/update_gear/<gear_id>', methods=["POST"])
def update_gear(gear_id):
    gear = mongo.db.gear
    gear.update({'_id': ObjectId(gear_id)},
                {
        'model': request.form.get('model'),
        'brand': request.form.get('brand'),
        'category_name': request.form.get('category_name'),
        'description': request.form.get('description'),
        'score': request.form.get('score'),
        'img_url': request.form.get('img_url')
    })
    return redirect(url_for('get_gear'))

@app.route('/delete_gear/<gear_id>')
def delete_gear(gear_id):
    mongo.db.gear.remove({'_id': ObjectId(gear_id)})
    return redirect(url_for('get_gear'))
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
