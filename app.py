import os
import env
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json


app = Flask(__name__)

# MongoDB config
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Collections
category_collection = mongo.db.category_collection
recipes_collection = mongo.db.recipes_collection
allergens_collection = mongo.db.allergens_collection
cuisine_collection = mongo.db.cuisine_collection

######################################################################
#                             RECIPES
######################################################################
@app.route('/')
@app.route('/recipes')
def get_recipes():
    return render_template("recipes.html", 
                            recipes=recipes_collection.find(),
                            allergens=allergens_collection.find(),
                            cuisine=cuisine_collection.find())


@app.route('/addRecipe')
def add_recipe():
    _categories = category_collection.find()
    category_list = [category for category in _categories]
    _allergens = allergens_collection.find()
    allergen_list = [allergen for allergen in _allergens]
    _cuisines = cuisine_collection.find()
    cuisine_list = [cuisine for cuisine in _cuisines]
    return render_template('add_recipe.html',
                            categories=category_list,
                            allergens=allergen_list,
                            cuisines=cuisine_list)


@app.route('/insertRecipe', methods = ['POST'])
def insert_recipe():
    
    form_request_to_dict = request.form.to_dict()
    # as allergens collected from checboxes add them to list
    form_request_to_dict['allergens'] = request.form.getlist('allergens')
    # split ingredients to create list of them
    form_request_to_dict['ingredients'] = form_request_to_dict['ingredients'].split(",")    
    # add keys to dictionary to be used when searching and sorting
    form_request_to_dict['views'] = 0
    form_request_to_dict['upvotes'] = 0
    form_request_to_dict['upvotes_who'] = []

    print(form_request_to_dict)

    recipes = recipes_collection
    recipes.insert_one(form_request_to_dict)
    
    return redirect(url_for('get_recipes'))


@app.route('/viewRecipe/<recipe_id>')
def view_recipe(recipe_id):
    recipe = recipes_collection.find_one({"_id": ObjectId(recipe_id)})
    return render_template("view_recipe.html", 
                            recipe=recipe)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'),
            debug=True)
