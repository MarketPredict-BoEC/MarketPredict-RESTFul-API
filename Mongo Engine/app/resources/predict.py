from flask import request, json, Response
from flask_restful import Resource
from flask_apispec import marshal_with
from app.response import ResponseAPI
from app.errors import CustomException
from app.model.predictModel import PredictModel
import logging as log
import json
from datetime import datetime


class Predict(Resource):
    @classmethod
    #@marshal_with(NewsModelSchema)
    def post(cls):
        try:
            data = request.json
            log.info(data)
            predictModel = PredictModel()

            data = predictModel.validatData(data)
            if data:
                response = predictModel.save_to_DB(data)
                if response:
                        return ResponseAPI.send(status_code=200, message="Inserted successfully", data=str(response))
                else:
                        return ResponseAPI.send(status_code=404, message="Database Connection Error")
            else:
                    # 404 status code for duplicated news item
                return ResponseAPI.send(status_code=404, message="Database Connection Error")
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent parameters format!")

        except Exception:
            raise CustomException("user_error", 500, 2201)

    @classmethod
    def get(cls):
        try:
            args = request.args
            log.info(args)
            if args is None or args == {}:
                return ResponseAPI.send(status_code=400, message="Please provide request parameters information")

            else:
                obj1 = PredictModel()
                response = obj1.find_by_date_pair_category(pair = args['pair'],category= args['category'], timestamp=args['timestamp'])
                return ResponseAPI.send(status_code=200, message="Successful", data=response)
        except ValueError:
            return ResponseAPI.send(status_code=422, message="Inconsistent date format!", data=False)
