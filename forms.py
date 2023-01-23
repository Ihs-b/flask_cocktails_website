from wtforms import SubmitField, StringField, validators
from flask_wtf import FlaskForm


class AgeSubmitForm(FlaskForm):
    yes = SubmitField("Yes")
    no = SubmitField("No")


class ChoiceForm(FlaskForm):
    drink = SubmitField("Random Drink")
    alcohol = SubmitField("Search by the alcohol you have")


class AlcoholForm(FlaskForm):
    ingredient = StringField("Write your alcohol", [validators.Length(min=3, max=35)])
    ok = SubmitField("ok")
