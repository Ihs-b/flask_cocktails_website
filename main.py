from flask import Flask, render_template, url_for, redirect, request, blueprints
from flask_sqlalchemy import SQLAlchemy
import requests
from forms import ChoiceForm, AgeSubmitForm, AlcoholForm
from flask_wtf.csrf import CSRFProtect
import os
from sqlalchemy.sql.expression import func, select
from flask_paginate import Pagination, get_page_parameter, get_page_args

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


# post_db()


#
# def get_random_drink():
#     return get_drink_api(random_param)
#
#
# def drink_by_ingredient(ingredient):
#     drinks_data = get_drink_api(param=ingredient_param + ingredient)
#     drink_ids = []
#     for drink in drinks_data[:10]:
#         drink_id = drink["idDrink"]
#         drink_ids.append(drink_id)
#     return drink_ids
#
#
# def drink_by_id(drink_id):
#     return get_drink_api(param=id_param + drink_id)
#
#
# def format_drink_data(drinks_data):
#     dr_choice = {}
#     elements = ['strDrink', "strGlass", "strIngredient1", "strIngredient2", "strInstructions", "strDrinkThumb",
#                 "strMeasure1",
#                 "strMeasure2"]
#     # titles_list = ["Drink name", "Glass", "First ingredient", "Second ingredient", "Instructions",
#     #                "Drink image", "1st ingredient Measurements", "2nd ingredient Measurements"]
#     new_drink = Drinks(id=1, drink_name="", glass="", first_ingredient="", second_ingredient="",
#                        instructions="", drink_image="", first_ingredient_measurements="",
#                        second_ingredient_measurements="")
#     for element in elements:
#         # element = drinks_data[0][element]
#         if drinks_data[0][element] != "null":
#             # for title in titles_list:
#             # dr_choice.append(element)
#             # dr_choice[title] = drinks_data[0][element]
#             new_drink.title = element
#     print(new_drink)
#     return dr_choice


@app.route('/', methods=['GET', 'POST'])
def home():
    form = AgeSubmitForm()
    if form.validate_on_submit():
        if "yes" in request.form:
            return redirect(url_for("cocktails"))
    return render_template('index.html', form=form)


@app.route('/cocktails', methods=['GET', 'POST'])
def cocktails():
    x = False
    form = ChoiceForm()
    form1 = AlcoholForm()
    if form.validate_on_submit():
        if "drink" in request.form:
            random_row = db.session.query(Drinks).order_by(func.random()).first()
            return render_template("cocktails.html", drinks=random_row.__dict__, form=form)
        elif "alcohol" in request.form:
            x = True
        if form1.validate_on_submit():
            # drink_request = select(Drinks).where(Drinks.first_ingredient == form1.ingredient.data)
            drinks_request = Drinks.query.filter_by(first_ingredient=form1.ingredient.data).all()
            # drink_request = db.first_or_404(
            #     db.select(Drinks).filter_by(first_ingredient=form1.ingredient.data),
            #     description=f"There's no drink with {form1.ingredient.data}")
            for drinks in drinks_request:
                print(drinks)
            # drink_rows = []
            # with db.session.connection() as conn:
            #     for row in conn.execute(drink_request):
            #         # print(row)
            #         drink_rows.append(row)
            # except ValueError as e:
            #         y = False
            #         error_message = "We don't have that alcohol, check your spelling or write another one"
            #         return render_template('cocktails.html', form=form, form1=form1, x=x, error_message=error_message)
            #     else:
            #         drinks_data = []
            #         x = True
            #         # for drink_id in drink_ids:
            #         #     drink = drink_by_id(drink_id)
            #         #     drink_data = format_drink_data(drink)
            #             # print(type(drink_data))
            #             drinks_data.append(drink_data)
            #         search = False
            #         q = request.args.get('q')
            #         print(q)
            #         if q:
            #             search = True
            #         # page, per_page, offset = get_page_args()
            #         page = request.args.get("page", default=1, type=int)
            #         per_page = 1
            #         offset = (page - 1) * per_page
            #         # split_data = drinks_data[:2]
            #         pagesize = 1
            #         start = (page - 1) * pagesize
            #         end = page * pagesize
            #         split_data = drinks_data[start:end]
            #         pagination = Pagination(page=page, per_page=per_page, total=len(drinks_data), offset=offset,search=search,
            #                                 record_name="drinks_data")
            #             # page, per_page, offset = get_page_args()
            #             # fs_for_render = list.limit(per_page).offset(offset)
            return render_template('cocktails.html', form=form, form1=form1, x=x, drinks=drinks_request, pagination=None)
    return render_template('cocktails.html', form=form, form1=form1, x=x, pagination=None)


@app.route("/<alcohol>/<page>")
def drink_choice(page):
    return render_template('cocktails.html')


if __name__ == "__main__":
    app.run(debug=True)
