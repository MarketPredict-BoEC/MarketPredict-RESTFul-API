from flask import Blueprint
from flask_restful import Api
from app.resources.news import News
from app.resources.predict import Predict


BASE_BLUEPRINT = Blueprint("base", __name__)
api = Api(BASE_BLUEPRINT)

api.add_resource(News, "/news")
api.add_resource(Predict, "/predict")

