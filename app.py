import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import pygal
from pygal.style import LightSolarizedStyle
import json
import pprint
from operator import itemgetter


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
deleted_recipes_collection = mongo.db.deleted_recipes_collection
allergens_collection = mongo.db.allergens_collection
cuisine_collection = mongo.db.cuisine_collection


# Lists for selects
_categories = category_collection.find()
category_list = [category for category in _categories]
category_list_sorted = sorted(category_list, key=itemgetter('category_name'))

_allergens = allergens_collection.find()
allergen_list = [allergen for allergen in _allergens]

_cuisines = cuisine_collection.find()
cuisine_list = [cuisine for cuisine in _cuisines]
cuisine_list_sorted = sorted(cuisine_list, key=itemgetter('cuisine_name'))

# global variables used to share data between edit_recipe and update_recipe
author_global = "None!"
views_global = 0
upvotes_global = 0
upvotes_who_global = []
filtered_and_excluded_allergens = []
searchedRecipes = []


######################################################################
#              RECIPES VIEW, SEARCH, FILTER ...
######################################################################


@app.route('/')
@app.route('/index')
def index():
    viewer = 'anonim'
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        print("USER: ", user_in_db['username'])
        if user_in_db:
            viewer = user_in_db['username']
    return render_template("index.html",
                           title="COOKBOOK",
                           viewer=viewer)

############################### RECIPES ###############################


@app.route('/recipes')
def get_recipes():
    viewer = 'anonim'
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        print("USER: ", user_in_db['username'])
        if user_in_db:
            viewer = user_in_db['username']

    # Pagination
    # Request the limit from link
    p_limit = int(request.args['limit'])

    # Request the offset from link
    # make sure is 0 or more to avoid server error
    p_offset = int(request.args['offset'])
    if p_offset < 0:
        p_offset = 0
    # make sure  is not bigger or equal than recipes count
    recipes_total = recipes_collection.find().count()
    if p_offset > recipes_total:
        p_offset = recipes_total

    # Default sort by ID >> greater id for last added to dbase
    recipes = list(recipes_collection.find().sort(
        '_id').limit(p_limit).skip(p_offset))
    return render_template("recipes.html",
                           allergens=allergens_collection.find(),
                           categories=category_list_sorted,
                           count=recipes_total,
                           cuisines=cuisine_list_sorted,
                           next_url=f"/recipes?limit={str(p_limit)}&offset={str(p_offset + p_limit)}",
                           p_limit=p_limit,
                           p_offset=p_offset,
                           prev_url=f"/recipes?limit={str(p_limit)}&offset={str(p_offset - p_limit)}",
                           recipes=recipes,
                           title="ALL Recipes",
                           viewer=viewer)

############################### VIEW RECIPE ###############################


@app.route('/viewRecipe/<recipe_id>')
def view_recipe(recipe_id):
    viewer = 'anonim'
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:
            viewer = user_in_db['username']
    # flash(viewer)
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    # Add and update (+1) to recipe.views
    views = recipe['views']
    views += 1
    recipes_collection.update({'_id': ObjectId(recipe_id)}, {
                              "$set": {'views': views}})
    upvotes_who = list(recipe['upvotes_who'])

    # keep info for jinja login in template to allow upvote or not
    if viewer in upvotes_who:
        voted_up_by_viewer = True
    else:
        voted_up_by_viewer = False

    # adjust youtube link to allow to be embeded on page
    keySentence1 = "youtu.be/"  # youtuube link from android app
    keySentence2 = "watch?v="  # youtube link from web browser
    leftPartOfLink = "https://www.youtube.com/embed/"  # left part of valid link

    # create right part of link
    def substring_after(youtubeLink, delim, delim1, many):
        if delim in youtubeLink:
            # youtuube link from android app
            after = youtubeLink.partition(delim)[2]
            return str(leftPartOfLink + (after[:many]))
        elif delim1 in youtubeLink:
            # youtube link from web browser
            after = youtubeLink.partition(delim1)[2]
            return str(leftPartOfLink + (after[:many]))
        else:
            # if cannot find keySentence1 or keySentence2 in link provided (probably invalid yoytube link)
            # do not display video in template
            return None

    recipe_video = substring_after(
        recipe['youtube'], keySentence1, keySentence2, 11)

    return render_template("view_recipe.html",
                           recipe=recipe,
                           recipe_video=recipe_video,
                           title="View Recipe",
                           viewer=viewer,
                           voted_up_by_viewer=voted_up_by_viewer)

############################### VOTE UP RECIPES ###############################


@app.route('/voteUp/<recipe_id>/<viewer>')
def vote_up(recipe_id, viewer):
    # Add viewer name to upvotes_who[]
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    upvotes_who = list(recipe['upvotes_who'])
    upvotes_who.append(viewer)
    # Add (+1) to recipe.upvotes
    print(recipe['upvotes'])
    recipe_upvotes = recipe['upvotes']
    recipe_upvotes += 1
    print(recipe_upvotes)

    recipes_collection.update({'_id': ObjectId(recipe_id)}, {
                              "$set": {'upvotes': recipe_upvotes, 'upvotes_who': upvotes_who}})

    users_collection.update({'username': viewer}, {
                            "$push": {'upvoted_recipes': recipe_id}})

    flash("Recipe Upvoted")
    return redirect(request.referrer)

############################### VOTE DOWN RECIPE ###############################


@app.route('/removeVoteUp/<recipe_id>/<viewer>')
def remove_vote_up(recipe_id, viewer):
    # Remove viewer name to upvotes_who[]
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    upvotes_who = list(recipe['upvotes_who'])
    upvotes_who.remove(viewer)
    # Subtract (-1) from recipe.upvotes
    print(recipe['upvotes'])
    recipe_upvotes = recipe['upvotes']
    recipe_upvotes -= 1
    print(recipe_upvotes)

    recipes_collection.update({'_id': ObjectId(recipe_id)}, {
                              "$set": {'upvotes': recipe_upvotes, 'upvotes_who': upvotes_who}})

    users_collection.update({'username': viewer}, {
                            "$pull": {'upvoted_recipes': recipe_id}})

    flash("Removed Recipe Upvote :(")
    return redirect(request.referrer)

############################### FILTER RECIPES ###############################


@app.route('/filterRecipes', methods=['GET', 'POST'])
def filter_recipes():

    if request.method == 'POST':
        form = request.form.to_dict()
        if 'action' in form:
            del form['action']
        if 'allergens' in form:
            form['allergens'] = request.form.getlist('allergens')

        # Create a temporary lists for storing filters and exclusions
        filters = list()
        exclusion = list()
        # Loop through each of the form keys
        for key in form:
            # Create temporary dictionary to which will be our single filter
            search_filter = dict()
            # Create new k,v pairs in above dictionary
            if key == 'allergens':
                items = form[key]
                for item in items:
                    exclusion.append(item)
            else:
                search_filter[key] = form[key]
                filters.append(search_filter)

        print(
            f"Filter (category or cuisine) :{filters}) | Filters (exclude allergens) :{exclusion}")

        # check if selectoin made - if not - display warning
        if filters or exclusion:
            # Create 2 queries
            recipes_with_allowed_allergens = list(recipes_collection.aggregate([
                {"$match": {"$and": [{'allergens': {"$nin": exclusion}}]}}]))
            if filters:
                recipes_filtered = list(recipes_collection.aggregate(
                    [{"$match": {"$and": filters}}]))
            # combine results having common part in recipes_filtered and recipes_with_allowed_allergens
            # keep results globally for pagination
            global filtered_and_excluded_allergens
            filtered_and_excluded_allergens = []
            if filters:
                for item in recipes_with_allowed_allergens:
                    if item in recipes_filtered:
                        filtered_and_excluded_allergens.append(item)
            else:
                filtered_and_excluded_allergens = recipes_with_allowed_allergens
            # pagination for first page only
            p_offset = 0
            count = len(filtered_and_excluded_allergens)

            p_limit = 8
            recipes = (filtered_and_excluded_allergens)[
                p_offset:p_limit+p_offset]

            return render_template("recipes.html",
                                   allergens=allergens_collection.find(),
                                   categories=category_list_sorted,
                                   count=count,
                                   cuisines=cuisine_list_sorted,
                                   next_url=f"/filterRecipes?limit={str(p_limit)}&offset={str(p_offset + p_limit)}",
                                   prev_url=f"/filterRecipes?limit={str(p_limit)}&offset={str(p_offset - p_limit)}",
                                   p_limit=p_limit,
                                   p_offset=p_offset,
                                   recipes=recipes,
                                   title="Filtered Recipes")
        else:
            flash("Choose something before hit FILTER")
            return redirect(request.referrer)
    else:
        # Pagination
        # Request the limit from link
        p_limit = int(request.args['limit'])
        # Request the offset from link
        # make sure is 0 or more to avoid erver error
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        # make sure  is not bigger or equal than recipes count
        count = len(filtered_and_excluded_allergens)
        if p_offset > count:
            p_offset = count

        recipes = (filtered_and_excluded_allergens)[p_offset:p_limit+p_offset]

        return render_template("recipes.html",
                               allergens=allergens_collection.find(),
                               categories=category_list_sorted,
                               count=count,
                               cuisines=cuisine_list_sorted,
                               next_url=f"/filterRecipes?limit={str(p_limit)}&offset={str(p_offset + p_limit)}",
                               prev_url=f"/filterRecipes?limit={str(p_limit)}&offset={str(p_offset - p_limit)}",
                               p_limit=p_limit,
                               p_offset=p_offset,
                               recipes=recipes,
                               title="Filtered Recipes")

############################### SEARCH RECIPES ###############################


@app.route('/searchRecipes', methods=['GET', 'POST'])
def search_recipes():

    if request.method == 'POST':
        form = request.form.to_dict()
        if 'action' in form:
            del form['action']
        inMealWord = form['word_in_meal']
        inIngredWord = form['word_in_ingredient']

        if not (inMealWord == '' and inIngredWord == ''):

            global searchedRecipes
            searchedRecipes = []
            # options i for case insensitive
            searchedRecipes = list(recipes_collection.find({"$and": [{'meal': {'$regex': inMealWord, '$options': 'i'}}, {
                                   'ingredients': {'$regex': inIngredWord, '$options': 'i'}}]}))
            p_offset = 0
            count = len(searchedRecipes)

            p_limit = 8
            recipes = (searchedRecipes)[p_offset:p_limit+p_offset]

            print(
                f"Type of results is  {type(searchedRecipes)} and it has {len(searchedRecipes)} items")
            return render_template("recipes.html",
                                   allergens=allergens_collection.find(),
                                   categories=category_list_sorted,
                                   count=count,
                                   cuisines=cuisine_list_sorted,
                                   next_url=f"/searchRecipes?limit={str(p_limit)}&offset={str(p_offset + p_limit)}",
                                   prev_url=f"/searchRecipes?limit={str(p_limit)}&offset={str(p_offset - p_limit)}",
                                   p_limit=p_limit,
                                   p_offset=p_offset,
                                   recipes=recipes,
                                   title="Searched Recipes")

        else:
            flash("Type in something before hit SEARCH")
            return redirect(request.referrer)
    else:
        # Pagination
        # Request the limit from link
        p_limit = int(request.args['limit'])
        # Request the offset from link
        # make sure is 0 or more to avoid erver error
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        # make sure  is not bigger or equal than recipes count
        count = len(searchedRecipes)
        if p_offset > count:
            p_offset = count

        recipes = (searchedRecipes)[p_offset:p_limit+p_offset]

        return render_template("recipes.html",
                               allergens=allergens_collection.find(),
                               categories=category_list_sorted,
                               count=count,
                               cuisines=cuisine_list_sorted,
                               next_url=f"/searchRecipes?limit={str(p_limit)}&offset={str(p_offset + p_limit)}",
                               prev_url=f"/searchRecipes?limit={str(p_limit)}&offset={str(p_offset - p_limit)}",
                               p_limit=p_limit,
                               p_offset=p_offset,
                               recipes=recipes,
                               title="Searched Recipes")

############################### ADD RECIPE ###############################


@app.route('/addRecipe')
def add_recipe():
        # Check if user is logged in
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:

            return render_template('add_recipe.html',
                                   allergens=allergen_list,
                                   author_passed_in=user_in_db,
                                   categories=category_list_sorted,
                                   cuisines=cuisine_list_sorted,
                                   title="Add Recipe")
        else:
            # user in session but not in database
            flash("Your session name is not in databse!")
            return render_template("login.html", title="Login")
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
    # add extra keys to dictionary
    form_request_to_dict['views'] = 0
    form_request_to_dict['upvotes'] = 0
    form_request_to_dict['upvotes_who'] = []
    # add Author manually as doesnt transfer from form when disabled
    form_request_to_dict['author'] = session['user']

    recipes = recipes_collection
    recipes.insert_one(form_request_to_dict)

    return redirect(url_for('index'))

############################### EDIT RECIPE ###############################


@app.route('/editRecipe/<recipe_id>')
def edit_recipe(recipe_id):
    # Check if user is logged in
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:
            the_recipe = recipes_collection.find_one(
                {"_id": ObjectId(recipe_id)})
            global author_global
            author_global = the_recipe['author']
            if user_in_db['username'] == author_global or user_in_db['username'] == 'admin':
                global views_global
                views_global = the_recipe['views']
                global upvotes_global
                upvotes_global = the_recipe['upvotes']
                global upvotes_who_global
                upvotes_who_global = list(the_recipe['upvotes_who'])

                
                ingredients_list_to_string = (
                    ','.join(the_recipe['ingredients']))

                return render_template('edit_recipe.html',
                                       allergens=allergen_list,
                                       author_passed_in=author_global,
                                       categories=category_list_sorted,
                                       cuisines=cuisine_list_sorted,
                                       ingredients_string=ingredients_list_to_string,
                                       recipe=the_recipe,
                                       title="Edit Recipe")
            else:
                # user is not an author or admin
                flash("user is not an author!")
                return redirect(url_for('index'))
        else:
            # user in session but not in database
            flash("Your session name is not in databse!")
            return redirect(url_for('index'))
    else:
        # Render the page for user to be able to log in
        flash("Please log in first!")
        return redirect(url_for('index'))

############################### UPDATE RECIPE ###############################


@app.route('/updateRecipe/<recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    form_request_to_dict = request.form.to_dict()
    form_request_to_dict['ingredients'] = form_request_to_dict['ingredients'].split(
        ",")

    recipes_collection.update({'_id': ObjectId(recipe_id)},
                              {
        'meal': request.form.get('meal'),
        'category': request.form.get('category'),
        'author': author_global,
        'upvotes': upvotes_global,
        'views': views_global,
        'upvotes_who': upvotes_who_global,
        'cuisine': request.form.get('cuisine'),
        'ingredients': list(request.form.get('ingredients').split(",")),
        'instructions': request.form.get('instructions'),
        'allergens': request.form.getlist('allergens'),
        'youtube': request.form.get('youtube'),
        'photo': request.form.get('photo')
    })
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

############################### DELETE RECIPE ###############################


@app.route('/deleteRecipe/<recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):

    # Before destroying document copy it to trash (deleted) with original id
    recipe_to_be_deleted = recipes_collection.find(
        {'_id': ObjectId(recipe_id)})
    deleted_recipes_collection.insert(recipe_to_be_deleted)
    # Delete pernamently from recipes_collection
    recipes_collection.remove({'_id': ObjectId(recipe_id)})

    return redirect(url_for('index'))


######################################################################
#                             USER AUTH
######################################################################

############################### LOGIN ###############################

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

############################### USER AUTH ###############################


@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    form['username'] = form['username'].lstrip().rstrip()
    user_in_db = users_collection.find_one({"username": form['username']})
    # Search for user in database
    if user_in_db:
        # If passwords match (hashed / real password)
        if check_password_hash(user_in_db['password'], form['user_password']):
            # Log user in (add to session)
            session['user'] = form['username']
            flash("You were logged in")
            return redirect(url_for('profile', user=user_in_db['username']))
        else:
            flash("Wrong password or user name")
            return redirect(url_for('login'))
    else:
        flash("Wrong password or user name")
        return redirect(url_for('login'))

############################### REGISTER ###############################


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is not logged in already
    if 'user' in session:
        flash('You are already signed in!')
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = request.form.to_dict()
        form['username'] = form['username'].lstrip().rstrip()
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

############################### LOG OUT ###############################


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You were logged out!")
    return redirect(url_for('index'))

############################### PROFILE PAGE ###############################


@app.route('/profile/<user>')
def profile(user):
    # Check if user is not logged in already
    if user == session['user']:
        # if 'user' in session:
        print(user)
        print(session['user'])
        # If so get the user and pass him to template for now
        user_in_db = users_collection.find_one({"username": user})
        # prepare list of recipes created by user
        profile_user_recipes = recipes_collection.find(
            {'author': user_in_db['username']}).sort('meal')
        # if == 0 change to None to avoid displaying Header in profile template as jinja is looking for it
        if profile_user_recipes.count() == 0:
            profile_user_recipes = None
        # to avoid error escape if user has no list of ids of upvoted recipes in his document
        try:
            upvoted_recipes_ids = user_in_db['upvoted_recipes']
        except:
            return render_template('profile.html',
                                   profile_user_recipes=profile_user_recipes,
                                   title="Profile",
                                   user=user_in_db)

        # if user document contain upvoted recipes ids prepare list pull each id and create list of recipes documents
        upvoted_recipes = []
        for id in upvoted_recipes_ids:
            # Upvoted recipes in user collection out of sync.
            # Admin or owner of one of recipes removed recipe...
            try:
                recip = recipes_collection.find_one({"_id": ObjectId(id)})
                upvoted_recipes.append(recip)
            except:
                # to do : remove invalid entry from document array
                pass
        # remove None values from list if exist
        upvoted_recipes = [x for x in upvoted_recipes if x is not None]
        upvoted_recipes = sorted(upvoted_recipes, key=itemgetter('meal'))

        return render_template('profile.html',
                               profile_user_recipes=profile_user_recipes,
                               title="Profile",
                               upvoted_recipes=upvoted_recipes,
                               user=user_in_db)
    else:
        flash("You must be logged in or You access wrong link...")
        return redirect(url_for('index'))


############################### ERROR 400 ###############################


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html', title="400"), 400


############################### ERROR 404 ###############################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title="404"), 404

############################### ERROR 500 ###############################


@app.errorhandler(500)
def internal_server_error(e):
    session.clear()
    return render_template('500.html', title="500"), 500

######################################################################
#                             GRAPHS
######################################################################


@app.route('/chart')
def chart():

    # Request the chart key from link
    count_key = str(request.args['count_key'])

    distinctKey = (recipes_collection.distinct(str(count_key)))
    distinctKey.sort()
    print(len(distinctKey))
    chart = pygal.Bar(print_values=True,
                      print_values_position='top',
                      legend_at_bottom=True,
                      style=LightSolarizedStyle(value_font_family='googlefont:Raleway',
                                                value_font_size=20,
                                                value_colors=()))
    chart.title = f"Recipes count by {count_key}"

    for item in distinctKey:
        count = recipes_collection.find({count_key: item}).count()
        chart.add(item, count)
        print(item, count)

    return render_template('graph.html', graph=chart.render_data_uri(), title="Graphs")


@app.route('/chartComplex')
def chart_complex():

    # Request the x and y streams from link
    factor_x = str(request.args['factor_x'])
    factor_y = str(request.args['factor_y'])

    factor_x_list = (recipes_collection.distinct(factor_x))
    factor_x_list.sort()

    factor_y_list = (recipes_collection.distinct(factor_y))
    factor_y_list.sort()

    line_chart = pygal.Line(x_label_rotation=45,
                            interpolate='hermite',
                            legend_at_bottom=True,
                            show_x_guides=True,
                            style=LightSolarizedStyle(value_font_family='googlefont:Raleway',
                                                      value_font_size=20,
                                                      value_colors=('black',)))
    line_chart.title = f"Recipes count by  {factor_x} in {factor_y}"

    print(factor_y_list)
    line_chart.x_labels = factor_y_list

    for x in factor_x_list:
        counts = []

        for y in factor_y_list:
            # for each factor_x_list member create list of count of each factor_y_list member
            count = recipes_collection.find(
                {"$and": [{factor_x: x}, {factor_y: y}]}).count()
            counts.append(count)
        # eg output > Basia [6, 1, 8, 9, 4, 1, 1, 1, 4, 0, 0, 0, 5]    
        print(x, counts)
        line_chart.add(x, counts)

    line_chart.render()

    return render_template('graph.html', graph=line_chart.render_data_uri(), title="Graphs")

######################################################################
#                             MAIN APP
######################################################################


if __name__ == '__main__':
    if os.environ.get("DEVELOPMENT"):
        print("DEVELOPMENT")
        app.run(host=os.environ.get('IP'),
                port=os.environ.get('PORT'),
                debug=True)
    else:
        print("NOT A DEVELOPMENT")
        app.run(host=os.environ.get('IP'),
                port=os.environ.get('PORT'),
                debug=False)
