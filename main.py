import os
import requests
from flask import Flask, render_template, url_for, redirect, request
from flask_paginate import Pagination, get_page_args
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql.expression import func, select

from forms import ChoiceForm, AgeSubmitForm, AlcoholForm

db = SQLAlchemy()
app = Flask(__name__)
csrf = CSRFProtect(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alcohol_drinks.db"
db.init_app(app)


class Drinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drink_name = db.Column(db.String, nullable=False)
    glass = db.Column(db.String, nullable=False)
    first_ingredient = db.Column(db.String, nullable=False)
    second_ingredient = db.Column(db.String, nullable=False)
    third_ingredient = db.Column(db.String)
    fourth_ingredient = db.Column(db.String)
    instructions = db.Column(db.String, nullable=False)
    drink_image = db.Column(db.String, nullable=False)
    first_ingredient_measurements = db.Column(db.String)
    second_ingredient_measurements = db.Column(db.String)
    third_ingredient_measurements = db.Column(db.String)
    fourth_ingredient_measurements = db.Column(db.String)


# with app.app_context():
#     db.create_all()

cocktail_url = 'https://www.thecocktaildb.com/api/json/v1/1/'

random_param = "random.php"
ingredient_param = "filter.php?i="
id_param = "lookup.php?i="
letter_param = "search.php?f=d"


def get_drink_api(param):
    response = requests.get(url=cocktail_url + param)
    data = response.json()["drinks"]
    return data


def post_db():
    data = get_drink_api(param=letter_param)
    with app.app_context():
        # # elements = ['strDrink', "strGlass", "strIngredient1", "strIngredient2", "strIngredient3", "strIngredient4",
        #             "strInstructions", "strDrinkThumb",
        #             "strMeasure1", "strMeasure2", "strMeasure3", "strMeasure4"]
        for drink in data:
            new_drink = Drinks(drink_name=drink['strDrink'], glass=drink['strGlass'],
                               first_ingredient=drink["strIngredient1"], second_ingredient=drink["strIngredient2"],
                               third_ingredient=drink["strIngredient3"], fourth_ingredient=drink["strIngredient4"],
                               instructions=drink["strInstructions"], drink_image=drink["strDrinkThumb"],
                               first_ingredient_measurements=drink["strMeasure1"],
                               second_ingredient_measurements=drink["strMeasure2"],
                               third_ingredient_measurements=drink["strMeasure3"],
                               fourth_ingredient_measurements=drink["strMeasure4"])
            db.session.add(new_drink)
            db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    age_form = AgeSubmitForm()
    if age_form.validate_on_submit():
        if "yes" in request.form:
            return redirect(url_for("cocktails"))
    return render_template('index.html', form=age_form)


@app.route('/cocktails', methods=['GET', 'POST'])
def cocktails():
    form = ChoiceForm()
    form1 = AlcoholForm()
    drinks_request = None
    drink_paginate = None
    ingredient = request.args.get("ingredient", type=str)
    page = request.args.get("page", default=1, type=int)
    x = True
    if form.validate_on_submit():
        if "drink" in request.form:
            return redirect(url_for("random_cocktail"))
        elif "alcohol" in request.form:
            # return redirect(url_for("drink_choice", page=1))
            x = False
        if form1.validate_on_submit():
            # page = request.args.get("page", default=1, type=int)
            # print(page)
            x = False
            # drink_request = select(Drinks).where(Drinks.first_ingredient == form1.ingredient.data)
            ingredient = form1.ingredient.data.title()
            drinks_request = Drinks.query.filter_by(first_ingredient=ingredient)
            drink_paginate = drinks_request.paginate(page=page, per_page=1)
            # return render_template('cocktails.html', form=form, form1=form1, x=x, drinks=drinks_request)
    else:
        if ingredient:
            drinks_request = Drinks.query.filter_by(first_ingredient=ingredient)
            drink_paginate = drinks_request.paginate(page=page, per_page=1)
    return render_template('cocktails.html', form=form, form1=form1, x=x, drinks=drinks_request, pages=drink_paginate, ingredient=ingredient)


@app.route("/yourcocktails", methods=['GET', 'POST'])
def random_cocktail():
    print("hello this is random cocktail")
    random_row = db.session.query(Drinks).order_by(func.random()).first()
    print(random_row)
    return render_template("random_drinks.html", drinks=random_row)


@app.route("/cocktails/<ingredient>", methods=["GET", "POST"])
def drinks_list(ingredient):
    page = request.args.get("page", 1, type=int)
    # if form1.validate_on_submit():
    #     x = False
    #     # drink_request = select(Drinks).where(Drinks.first_ingredient == form1.ingredient.data)
    #     ingredient = form1.ingredient.data.title()
    #     drinks_request = Drinks.query.filter_by(first_ingredient=ingredient).paginate(page=page, per_page=2)
    # return render_template('cocktails.html', form=form, form1=form1, x=x, drinks=drinks_request)


if __name__ == "__main__":
    app.run(debug=True)
