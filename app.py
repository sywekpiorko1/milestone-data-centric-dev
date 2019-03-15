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
recipes_collection = mongo.db.recipes_collection
allergens_collection = mongo.db.allergens_collection
cuisine_collection = mongo.db.cuisine_collection

# Main routes 
@app.route('/')
@app.route('/recipes')
def get_recipes():
    return render_template("recipes.html", recipes=recipes_collection.find(),
                            allergens=allergens_collection.find(),
                            cuisine=cuisine_collection.find())


# Backup collections (by CI Miro_lead)
# @app.route('/backup')
# def do_backup_to_json_file():
#     # This will be the JSON
#     backup = {}
#     # Your collections goes here
#     data = [recipes_collection.find(), allergens_collection.find(),
# 		cuisine_collection.find()]

#     for collection in data:
# 	    # Create new list in the dict with key like '1' for example
# 	    backup[f'{len(backup) + 1}'] = []
# 	    for x in collection:
# 		    del x['_id']
# 		    # Add the document to the key ... 
# 		    backup[f'{len(backup)}'].append(x)

# print(backup)

# with open('backup.json', 'w') as outfile:
# 	json.dump(backup, outfile)
	
# At the end you will end up with something like 
"""
{
	'1' : [document,document, document, document],
	'2' : [document,document, document, document],	
	'3' : [document,document, document, document]
}
"""

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'),
            debug=True)