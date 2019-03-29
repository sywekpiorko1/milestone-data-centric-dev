import os
import env
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import json
import pprint

app = Flask(__name__)

# MongoDB config
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)
pp = pprint.PrettyPrinter(indent=4)

# Collections
users_collection = mongo.db.users_collection
category_collection = mongo.db.category_collection
recipes_collection = mongo.db.recipes_collection
allergens_collection = mongo.db.allergens_collection
cuisine_collection = mongo.db.cuisine_collection


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


######################################################################
#                             RECIPES
######################################################################


@app.route('/recipes')
def get_recipes():
    return render_template("recipes.html",
                           title="Recipes",
                           recipes=recipes_collection.find(),
                           allergens=allergens_collection.find(),
                           cuisine=cuisine_collection.find(),
                           category=category_collection.find())


@app.route('/searchRecipes', methods=['GET', 'POST'])
def search_recipes():
    if request.method == 'POST':
        form = request.form.to_dict()
        # Create list of values for Cuisine and Category multiselection
        if len(request.form.getlist('cuisine')) > 0:
            form['cuisine'] = request.form.getlist('cuisine')
        if len(request.form.getlist('category')) > 0:
            form['category'] = request.form.getlist('category')
        # remove action key from dictionary
        if 'action' in form:
            del form['action']

        # debug
        print("pp.pprint(form)"),
        pp.pprint(form)

        # Create a temporary list for stoing the filters
        filters = list()
        # Loop through each of the keys from form
        for key in form:
            # Loop through list of values
            for value in form[key]:
                print(key, " ", value)
                # Create temporary dictionary to which will be our single filter
                # Each filter MUST be a valid dictionary
                search_filter = dict()
                # Create new k,v pars in above dictionary
                # {"cuisines" : "asian"}
                search_filter[key] = value
                # Append then new created filter to our list of filters
                filters.append(search_filter)
                print("print(search_filter)"),
                print(search_filter)
                # should be for ex. {'cuisine': 'Greek'}

        # Create single query with 1 or more filters
        print("print(filters)"),
        print(filters)
        # should be like format: [{'cuisine': 'Greek'}, {'category': 'Seafood'}]

        # Warning if no selection made
        if filters:
            recipes = recipes_collection.aggregate([
                {
                    "$match": {
                        "$or": filters
                    }
                }
            ])
        else:
            recipes = {}
            flash("Choose something before search!")

        return render_template('search.html', recipes=list(recipes),
                               cuisine=cuisine_collection.find(),
                               category=category_collection.find())
    return render_template('search.html',
                           cuisine=cuisine_collection.find(),
                           category=category_collection.find())


@app.route('/addRecipe')
def add_recipe():
        # Check if user is logged in
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:
            _categories = category_collection.find()
            category_list = [category for category in _categories]
            _allergens = allergens_collection.find()
            allergen_list = [allergen for allergen in _allergens]
            _cuisines = cuisine_collection.find()
            cuisine_list = [cuisine for cuisine in _cuisines]
            return render_template('add_recipe.html',
                                   title="Add Recipe",
                                   categories=category_list,
                                   allergens=allergen_list,
                                   cuisines=cuisine_list,
                                   author_passed_in=user_in_db)
        else:
            # user in session but not in database
            flash("Your session name is not in databse!")
    else:
        # Render the page for user to be able to log in
        flash("Please log in first!")
        return render_template("login.html", title="Login")


@app.route('/insertRecipe', methods=['POST'])
def insert_recipe():

    form_request_to_dict = request.form.to_dict()
    # as allergens collected from checboxes add them to list
    form_request_to_dict['allergens'] = request.form.getlist('allergens')
    # split ingredients to create list
    form_request_to_dict['ingredients'] = form_request_to_dict['ingredients'].split(
        ",")
    # add keys to dictionary to be used when searching and sorting
    form_request_to_dict['views'] = 0
    form_request_to_dict['upvotes'] = 0
    form_request_to_dict['upvotes_who'] = []
    # add Author manually as doesnt transfer from form when disabled
    form_request_to_dict['author'] = session['user']

    pp.pprint(form_request_to_dict)

    recipes = recipes_collection
    recipes.insert_one(form_request_to_dict)

    return redirect(url_for('get_recipes'))


@app.route('/viewRecipe/<recipe_id>')
def view_recipe(recipe_id):
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    return render_template("view_recipe.html",
                           title="View Recipe",
                           recipe=recipe)


######################################################################
#                             USER AUTH
######################################################################


@app.route('/login', methods=['GET'])
def login():
    # Check if user is not logged in already
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:
            # If so redirect user to his profile
            flash("You are logged in already!")
            return redirect(url_for('profile', user=user_in_db['username']))
    else:
        # Render the page for user to be able to log in
        return render_template("login.html", title="Login")


@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    user_in_db = users_collection.find_one({"username": form['username']})
    # Search for user in database
    if user_in_db:
        # If passwords match (hashed / real password)
        if check_password_hash(user_in_db['password'], form['user_password']):
            # Log user in (add to session)
            session['user'] = form['username']
            # If the user is admin redirect him to admin area
            if session['user'] == "admin":
                return redirect(url_for('admin'))
            else:
                flash("You were logged in!")
                return redirect(url_for('profile', user=user_in_db['username']))
        else:
            flash("Wrong password or user name")
            return redirect(url_for('login'))
    else:
        flash("You must be registered!")
        return redirect(url_for('register'))

# Register


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is not logged in already
    if 'user' in session:
        flash('You are already signed in!')
        return redirect(url_for('get_recipes'))
    if request.method == 'POST':
        form = request.form.to_dict()
        # Check if password and password1 match
        if form['user_password'] == form['user_password1']:
            # If so look for user in db
            user = users_collection.find_one({"username": form['username']})
            if user:
                flash(f"{form['username']} already exists!")
                return redirect(url_for('register'))
            # If user doesnt exist register new user
            else:
                # Hash password
                hash_pass = generate_password_hash(form['user_password'])
                # Create new user with hashed password
                users_collection.insert_one(
                    {
                        'username': form['username'],
                        'email': form['email'],
                        'password': hash_pass
                    }
                )
                # Check if user is saved
                user_in_db = users_collection.find_one(
                    {"username": form['username']})
                if user_in_db:
                    # Log user in (add to session)
                    session['user'] = user_in_db['username']
                    flash("You are registered now!")
                    return redirect(url_for('profile', user=user_in_db['username']))
                else:
                    flash("There was a problem saving your profile")
                    return redirect(url_for('register'))
        else:
            flash("Password dont match!")
            return redirect(url_for('register'))

    return render_template('register.html', title="Register")

# Log out


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You were logged out!")
    return redirect(url_for('index'))

# Profile page


@app.route('/profile/<user>')
def profile(user):
    # Check if user is not logged in already
    if 'user' in session:
        # If so get the user and pass him to template for now
        user_in_db = users_collection.find_one({"username": user})
        return render_template('profile.html', title="Profile", user=user_in_db)
    else:
        flash("You must be logged in!")
        return redirect(url_for('get_recipes'))

# Admin


@app.route('/admin')
def admin():
    if 'user' in session:
        if session['user'] == 'admin':
            return render_template('admin.html')
        else:
            flash('Only Admins can access this page!')
            return redirect(url_for('get_recipes'))
    else:
        flash('You must be logged in!')
        return redirect(url_for('get_recipes'))


if __name__ == '__main__':
    if os.environ.get("DEVELOPMENT"):
        app.run(host=os.environ.get('IP'),
                port=os.environ.get('PORT'),
                debug=True)
    else:
        app.run(host=os.environ.get('IP'),
                port=os.environ.get('PORT'),
                debug=False)
