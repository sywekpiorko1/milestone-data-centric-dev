# CookBook

## Introduction

I wish to introduce project which is the summary of Data Centric Development learning path - part of Full Stack Developer course by [Code Institute](https://codeinstitute.net)

I will try to demonstrate the knowledge needed to create a web application based on [Python 3](https://www.python.org/)  and the [Flask](http://flask.pocoo.org/) framework to perform operations to create, read, edit and delete records of data in the cloud [NoSQL](https://en.wikipedia.org/wiki/NoSQL) database [MongoDB](https://www.mongodb.com/) using 
free host [Atlas](https://www.mongodb.com/cloud/atlas)

## Code Institute Brief

- **CREATE AN ONLINE COOKBOOK**
  - Create a web application that allows users to store and easily access cooking recipes
  - Put some effort into designing a database schema based on recipes, and any other related properties and entities (e.g. views, upvotes, ingredients, recipe authors, allergens, author’s country of origin, cuisine etc…). Make sure to put some thought into the relationships between them, and use either foreign keys (in the case of a relational database) or nesting (in the case of a document store) to connect these pieces of data
  Create the backend code and frontend form to allow users to add new recipes to the site (at least a basic one, if you haven’t taken the frontend course)
  - Create the backend code to group and summarise the recipes on the site, based on their attributes such as cuisine, country of origin, allergens, ingredients, etc. and a frontend page to show this summary, and make the categories clickable to drill down into a filtered view based on that category. This frontend page can be as simple or as complex as you’d like; you can use a Python library such as matplotlib, or a JS library such as d3/dc (that you learned about if you took the frontend modules) for visualisation
  - Create the backend code to retrieve a list of recipes, filtered based on various criteria (e.g. allergens, cuisine, etc…) and order them based on some reasonable aspect (e.g. number of views or upvotes). Create a frontend page to display these, and to show some summary statistics around the list (e.g. number of matching recipes, number of new recipes. Optionally, add support for pagination, when the number of results is large
  - Create a detailed view for each recipes, that would just show all attributes for that recipe, and the full preparation instructions
  - Allow for editing and deleting of the recipe records, either on separate pages, or built into the list/detail pages
  - Optionally, you may choose to add basic user registration and authentication to the site. This can as simple as adding a username field to the recipe creation form, without a password (for this project only, this is not expected to be secure)

- **CREATE YOUR OWN PROJECT**
  - If you choose to create your project outside the brief, the scope should be similar to that of the example brief above.

## UX

- Barbara, she loves to cook, she uses notebooks and loose sheets to store recipes which is not very comfortable, besides often seeing the desire to make a change in the recipe is not able to carry it out on a current basis

The app will help her create her own recipe database with the possibility of easy and pleasant editing

## UI

I started with vision that the main window of the application will be a view of several recipes, then the user could enter the details of each recipe in a separate window, he could log in to be able to add the selected recipe to favorites, so that later on his profile page he could quickly find his favorite recipes together with the list of recipes created by him.

I took into account the creation of a page with graphic charts showing the statistics of the whole  recipe database in terms of the number of recipes of a given user, and the number of recipes depending on which category or cuisine belong.

An anonymous user could see all recipes, look for recipes for the word in the name or in the ingredients needed to comply with the recipe, he could also filter the recipes taking into account the exclusion of allergens, cuisine or category.

After registering / logging in, the user gains the opportunity to like the recipe of another author (but not his own), add his own recipe along with later editing, delete his own recipes, access to created and liked recipes on his profile page.

The administrator has user rights extended to the editions of all recipes and the ability to delete all recipes without the need for author's permission.
After analyzing the required fields of the database, I created a mongoDB schematic that I present in the [dbSchemas](/dbSchemas).

List of allergens, cuisines of the world and the categories of recipes I placed in separate collections so that might be looped by jinja code and pushed into the select inputs or checkboxes.

After adding the first few recipes, I started to create the search and filtering logic, then downloaded over 190 recipes with the help of a small python program, which further processed the data structure under my schemas.

I downloaded the recipes from [themealdb.com](https://www.themealdb.com/)

When the base grew to larger sizes it was necessary to add pagination, I decided to view eight,ten or twelve recipes on the page.

### Going to the description of the pages' appearance

The home page, which is displayed on the aplication root path or after clicking the `CookBook` icon, consists of three sliders on which kitchen fun facts are displayed.

Clicking `ALL RECIPES` in navbar will show us the page with recipes, in my mind I had a plan to use two - three rows in several columns to fill the screen fully but without excessive scrolling need, with the possibility of page flipping by chevrons.

In the initial version of the project I created a separate `FILTER` page without the ability to search for words, but it turned out to be uncomfortable due to switching the view between the filtered recipes and the filtering parameters template.

Then I placed the filtering panel above the recipes but after making such a pattern I noticed that it is too wide and I decided to move the panel to the left in the view on large screens.

![](static/images/readme/recipes_large_screen.jpg)

In the meantime, I enriched the `FILTER` panel with `SEARCH` functions.

In the filter part, the `FILTER` button is activated only when we make at least one choice, but the choices can be specified eg exclude allergens: `milk` and `wheat`, show only `Desert` category from `French` cuisine. The above criteria for the recipes database will show only one result.
You can select single choice of Cuisine and Category selection and multiple checkboxes in allergens all together.

In the search part, the `SEARCH` button is activated after entering at least 3 characters in the field `in meal name` or `in ingredient`. The narrowed result will be obtained after filling in both fields.

At any moment we can clear all fields by pressing the `RESET` button, the page will be reloaded, we will be presented with a full list of recipes.


In the mobile view, recipes are displayed in two columns without the `FILTER / SEARCH` panel visible by default.

In the bottom right corner there is a pulsing icon which when pressed displays the `FILTER / SEARCH` panel above the recipes. Once the panel is visible, the icon will hide so as not to interfere with the `FILTER / SEARCH` panel, it will be displayed again only when the page is reloaded or flipped with chevrons.

![](static/images/readme/recipes_mobile.jpg)

After pressing the `SHOW DETAILS` section on any of the recipes bottom part, You go to the single recipe view.
By default, a tab with ingredients is displayed - to see the preparation instructions, switch tab from the `INGREDIENTS` to `INSTRUCTIONS`.

In the `INSTRUCTIONS` tab below the steps of executing the recipe a window with the material on youtube is displayed.

When we are logged in, at the bottom of the single recipe view, we have the option of editing (if we are the author or admin), upvoting or removing ours upvote (if we are not the author) and deleting the recipe (as author or admin).
The deletion is preceded by a modal in which we can withdraw from the decision.
In general - recipe can be only upvoted (positive feedback), there is no negative impact on recipe, can be only neutral.

![](static/images/readme/single_recipe.jpg)

To add a new recipe you must be logged in.

If so it activates the options `ADD RECIPE` in navbar, which leads to the form where we give the name of the recipe, select the categories and cuisine, input the components separated by commas, prepare instructions separated by dots, check allergens known to us, fill in the yotube link fields and photo link using the correct www links.

After adding the recipe, it appears in the list on the user's profile page and completes the database.
Editing an existing recipe displays the same page as adding a recipe, however the fields are already filled out and we can edit them.

![](static/images/readme/add_update_recipe.jpg)

The `Graphs Page` page (lighting bolt like icon in navigator) allows us to read the statistics of the recipes for distribution by the author, category or kitchen - `yellow buttons`.

The `blue buttons` give a view of statistics for two criteria, e.g. `"Recipes count by author in category"`.

## To be implemented

- To create additional collections with data needed to display graphs directly, the data would be updated when changing the recipes parameters in a full database, eg when adding, removing or editing recipes. For example, in order to display "Country Reception by category in cisine" we need about 10 seconds to perform a double loop searching each time.

- Enter sorting for different criteria

- Enter better validation of data entered by users

- Use actively email addresses collected during registration, for example to activate an account after registration and to send notifications about new recipes to users who would agree to it.

- In pagination, I would like to add the possibility of displaying transitional page numbers to allow navigation not only to the next or previous page.

- Also add the option of contacting the admin to submit corrections. Admin would then display a list of corrections made in the log available to users through the appropriate link.

## Technologies Used

I started work and project in the [c9.io](https://c9.io/login) environment, but soon changed the environment to [vsCode](https://code.visualstudio.com/), in which I could easily debug the code without having to use the print() function often.

The application is written in [Python 3](https://www.python.org/downloads/), based on [Flask](http://flask.pocoo.org/) microframework, data is stored on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas), database queries sent using [PyMongo](https://flask-pymongo.readthedocs.io/en/latest/), graphs displayed thanks to the dynamic svg library - [Pygal](http://www.pygal.org/en/stable/).

I worked on the Windows 10 platform, I used the development tools of Chrome and Firefox browsers, I used android mobile phones and tablet.

To speed up the creation of the project I used css framework [Materialize 1.0.0](https://materializecss.com/).

Logo created using the https://logomakr.com/ website.

Favicon generated by [https://www.favicon-generator.org/](https://www.favicon-generator.org/).

## Testing

- The application was tested manually by me and the family that sent me a description of errors or screenshots of errors in the appearance of the site.

- I've introduced page templates 400, 404 and 500 to replace the unfriendly default appearance.

- I simulated attempts to enter without authorization on templates requiring authorization, to be sure to secure sensitive areas.

- I wish to describe things going bad on css materialize:

    - In the initial phase when I used materialize 0.100.2, I experienced that the checkboxes ceased to be clickable on some pages, I found a mention of such behavior on issues for that version of library, there was suggested a downgrade to version 0.98.0.

    - I did so but ultimately upgraded to version 1.0.0 to run correctly sliders on the title page

    - The next problem was displaying recipes in bulk using materialize cards:
        - Photos in the newly added recipes did not have a constant proportion as in the case of existing ones on [themealdb.com](https://www.themealdb.com/)
        - In this situation, the cards started to appear in wrong rows, because jinja used the loop of 8 recipes per page and did not switch to the next row after reaching the fourth recipe (for big screen view)
        - For this purpose, I used a js script that constantly attaches to and smoothly switches classes that bind the height of the photos.
- Responsiveness tested on devices with android system and in Chrome and Firefox development environment.

- I have used tools:

    - [W3C Markup Validation Service](https://validator.w3.org/)
    - [CSS W3C validation service](https://jigsaw.w3.org/css-validator/)
    - [vsCode Flask Debugger](https://code.visualstudio.com/docs/python/tutorial-flask)

## Deployment

I introduced version controls in the git system, and isolated the environment
Next, the application code after the introduction of key functionalities was sent independently to the [github repo](https://github.com/sywekpiorko1/milestone-data-centric-dev) and to the hosting of [heroku platform](https://signup.heroku.com/) to test behavior on an external server.

## To run application locally

Create [virtual environment](https://www.geeksforgeeks.org/python-virtual-environment/)

Create a mongodb database based on folder [dbSchemas](/dbSchemas)
- Create [recipes_collection](/dbSchemas/recipes_collection.json) (empty at the beginning)
- Create [category_collection](/dbSchemas/category_collection.json) (13 categories in my case)
- Create [cuisine_collection](/dbSchemas/cuisine_collection.json) (21 cuisines in my case)
- Create [allergens_collection](/dbSchemas/allergens_collection.json) (8 allergens in my case)
- Add an admin account and other users in the running application

Create a `.bashrc` file in the root of the user's directory

Create the following commands in it using the correct `password` and the name of Database (`recipes` in my case):
- `export MONGO_URI="mongodb+srv://root:[password]@mytestdb-12wi3.mongodb.net/recipes?retryWrites=true"`
- `export SECRET_KEY="secretKey"`
- `export IP="0.0.0.0"`
- `export PORT="5000"`
- `export DEVELOPMENT="1"`

then bind it with the application using (in the root application folder):
- $ `source ~/.bashrc`

Install the python 3+ environment and pip3 on your computer

Install the required libraries from the [requirements.txt](requirements.txt) file:

- $ `pip install -r requirements.txt`

We run application with the command:

- $ `python app.py`

whereas the command:

- $ `python –-version`

will give us the Python 3+ version.

To open application within the local network in the browser use the server's IP address and `5000` port, eg:

- `192.168.1.12:5000`

and on the same computer:

- `127.0.0.1:5000`

Globaly on the heroku platform , the application can be found at:

## [https://cookbook-sylpio.herokuapp.com/](https://cookbook-sylpio.herokuapp.com/)

In order to correctly execute applications on your own heroku account it is necessary to add config vars:
- `IP >	0.0.0.0`
- `MONGO_URI >	mongodb+srv://root:[password]@mytestdb-12wi3.mongodb.net/[database_name]?retryWrites=true`
- `PORT > 5000`
- `SECRET_KEY >	secretKey`

We omit the `DEVELOPMENT` variable in the production phase

## Acknowledgements

I used the slack application in the code institute room to keep track of the group working on their own projects

I used the knowledge provided in the forum github by the leader of the slack group > `Miroslav Svec` [https://github.com/MiroslavSvec/DCD_lead](https://github.com/MiroslavSvec/DCD_lead) in order to implement login, registration, password hashing and pagination

I actively used sources:

- [Stack overflow](https://stackoverflow.com/)
- [Materialize CSS](https://materializecss.com/)
- [Flask / Pocoo](http://flask.pocoo.org/docs/1.0/)
- [Miguel Grinberg blog](https://blog.miguelgrinberg.com/index)

The recipes and photos are from [themealdb.com](https://www.themealdb.com/)
Thanks to friends who took the time to test the application, their feedback was necessary to improve the image of this application