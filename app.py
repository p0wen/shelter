import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_pymongo import PyMongo
from datetime import date
from bson.objectid import ObjectId
import bcrypt
if os.path.exists("env.py"):
    import env

app = Flask('__name__')

""" Configuration of app from heroku .env file """

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

""" Global Variables """
mongo = PyMongo(app)
users = mongo.db.users
gear = mongo.db.gear
categories = mongo.db.categories

""" Indexing of Database to allow search functionality """
gear.create_index([
    ('model', 'text'),
    ('brand', 'text'),
    ('description', 'text'),
    ('category_name', 'text')
])

@app.route('/')
def index():
    """
    Collects featured posts,
    Collects the most recent gear postings
    Return collections for rendering the landing page
    """
    get_featured_posts = mongo.db.gear.aggregate(
        [{'$match': {'is_featured': True}},
         {'$sample': {'size': 3}}])
    gear_sorted = gear.find().sort("datecreated", -1).limit(6)
    return render_template("index.html", rdm_feat=list(get_featured_posts), gear_collection=list(gear_sorted), categories=list(categories.find()))


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Gets the username from the html form
    Checks if the entered Password is correct
    Give feedback if it fails
    Otherwise user will be forwarded to index page
    """
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':    
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            else:
                flash("Wrong password")
                return redirect(url_for('login'))

        flash("User does not exist")
        return redirect(url_for('login'))
    return render_template('login.html', categories=list(categories.find()))

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    """
    Handles the registration of a user
    Checks if chosen username is already taken 
    Encryptes the password before storing it to the Database
    Sets the username for the session for future identification
    """
    created_on = date.today()
    if request.method == 'POST':
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one(
                {'name': request.form['username'],
                 'password': hashpass,
                 'date_registered': created_on.isoformat(),
                 'is_admin': False
                 })
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash("That username already exists! Try another one")
            return render_template('signup.html', categories=list(categories.find()))
    return render_template('signup.html', categories=list(categories.find()))

# Function to logout existing users https://stackoverflow.com/questions/27747578/how-do-i-clear-a-flask-session


@app.route('/logout')
def logout():
    """

    """
    username = session['username']
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('login'))


@app.route('/', methods=["POST"])
def search():
    search_this_string = request.form['search']
    cursor = mongo.db.gear.find({"$text": {"$search": search_this_string}})
    return render_template('searchresults.html', 
                            result=list(cursor),
                            categories=list(mongo.db.categories.find()))


@app.route('/get_gear')
def get_gear():
    return render_template('gallery.html',
                           gear_collection=mongo.db.gear.find(),
                           categories=list(mongo.db.categories.find()))


@app.route('/add_gear')
def add_gear():
    return render_template('add_gear.html',
                           category_sel=mongo.db.categories.find(),
                           categories=list(mongo.db.categories.find()))


@app.route('/myprofile/<user>')
def myprofile(user):
    if 'username' in session:
        if session["username"] == user:
            myprofile = users.find_one({"name": user})
            user_postings = mongo.db.gear.find({'author': user})
            total_posts = user_postings.count()
            return render_template('myprofile.html',
                                   myprofile=myprofile,
                                   user_post=list(user_postings),
                                   total_posts=total_posts,
                                   categories=list(mongo.db.categories.find()))
            return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/delete_account/<user_id>')
def delete_account(user_id):
    if 'username' in session:
        if session["username"] == users.find_one({"_id": ObjectId(user_id)})['name']:
            del_acc = users.find_one(
                {"_id": ObjectId(user_id), "name": session["username"]})
            if del_acc:
                session.pop('username', None)
                users.remove({'_id': ObjectId(user_id)})
                return redirect(url_for('index'))
        return redirect(url_for('index'))
    return redirect(url_for('index'))


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
        'is_featured': False,
        'author': session['username']
    }
    gear.insert_one(new_doc)
    return redirect(url_for('get_gear'))


@app.route('/gear_details/<gear_id>')
def gear_details(gear_id):
    gear_details = mongo.db.gear.find_one({"_id": ObjectId(gear_id)})
    return render_template('gear_details.html', gear_details=gear_details, categories=list(mongo.db.categories.find()))


@app.route('/edit_gear/<gear_id>')
def edit_gear(gear_id):
    the_gear = mongo.db.gear.find_one({"_id": ObjectId(gear_id)})
    all_categories = mongo.db.categories.find()
    return render_template('edit_gear.html', gear=the_gear, category_sel=all_categories, categories=list(mongo.db.categories.find()))


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


@app.route('/about')
def about():
    return render_template('about.html', categories=list(mongo.db.categories.find()))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
