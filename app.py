import os
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_pymongo import PyMongo
from datetime import date
from bson.objectid import ObjectId

app = Flask('__name__')

app.config.from_object('env')

mongo = PyMongo(app)


mongo.db.gear.create_index([
     ('model', 'text'),
     ('brand', 'text'),
     ('description', 'text'),
     ('category_name', 'text')
])

@app.route('/')
@app.route('/index')
def index():
    gear = mongo.db.gear.find()
    cursor = mongo.db.gear.aggregate(
        [{'$match': {'is_featured': True}},
         {'$sample': {'size': 3}}])
    gear_sorted = gear.sort("datecreated", -1).limit(6)
    return render_template("index.html", rdm_feat=list(cursor), gear_collection=list(gear_sorted))


@app.route('/', methods=["POST"])
def search():
    search_this_string = request.form['search']
    cursor = mongo.db.gear.find({"$text": {"$search": search_this_string}})
    return render_template("searchresults.html", result=list(cursor))


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
    created_on = date.today()
    new_doc = {
        "datecreated": created_on.isoformat(),
        'model': request.form.get('model'),
        'brand': request.form.get('brand'),
        'category_name': request.form.get('category_name'),
        'description': request.form.get('description'),
        'score': request.form.get('score'),
        'img_url': request.form.get('img_url'),
        'is_featured': False
    }
    gear.insert_one(new_doc)
    return redirect(url_for('get_gear'))

@app.route('/gear_details/<gear_id>')
def gear_details(gear_id):
    gear_details = mongo.db.gear.find_one({"_id": ObjectId(gear_id)})
    return render_template('gear_details.html', gear_details=gear_details)

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
