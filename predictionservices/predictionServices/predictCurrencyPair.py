import pathlib
from datetime import datetime
from dataProvidingServices.dataProviding import prepairDataForLoad
from tensorflow.keras.models import load_model
import requests
import numpy as np
import errors
import json

Training = True


def roundTimestampToNearHour(ts):
    return ts - (ts % 3600)


def predict_model(category, pair, newsKeywords,
                  provider=['fxstreet'], concept_number=210,
                  resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                  ):
    try:
        # timezone utc
        endDate = int(datetime.utcnow().timestamp())
        endDate = roundTimestampToNearHour(endDate)
        marketDelayWindow = SEQ_LEN * 60 * 60
        print(datetime.fromtimestamp(endDate))
        startDate = endDate - marketDelayWindow
        # when we use this function for prediction , we dont set startDate because the calculation of indicators
        test_x, test_y, test_news_x, dates = prepairDataForLoad(category,
                                                                pair, startDate, endDate, newsKeywords=newsKeywords,
                                                                provider=provider, concept_number=concept_number,
                                                                resolution=resolution, SEQ_LEN=SEQ_LEN,
                                                                SEQ_LEN_news=SEQ_LEN_news,
                                                                max_L=max_L, Training=False, conceptsType=conceptsType)

        modelName = pair.upper() + 'WithNewsHourly.h5'
        current_Path = pathlib.Path().absolute()
        path = str(current_Path) + '/outputFiles/' + category + '/' + pair + '/' + modelName
        model = load_model(path)
        # todo: add model as parameter
        pred_train = model.predict([test_x, test_news_x])

        # check previous timestamp
        query = {"pair": pair, "timestamp": endDate,"category":'CryptoCurrency', 'resolution':'H'}
        url = 'http://localhost:5000/Robonews/v1/predict'
        resp = requests.get(url, params=query)
        data = json.loads(resp.text)
        data = data['data']
        print(data)
        if data['predictedPrice']:
            change = np.float(pred_train[0, 0]) - np.float(data['predictedPrice'])
        else:
            change = 0
        if change > 0:
            trend = "up"
        elif not change:
            trend = 'none'
        else:
            trend = "down"
        # add one hour : code only works or hourly resolution
        endDate = endDate + 3600
        data = {'category': category,
                'pair': pair,
                "change": change,
                "trend": trend,
                'timestamp': endDate,
                'predictedPrice': np.float(pred_train[0, 0]),
                'model': conceptsType,
                'resolution': resolution,
                }
        print(data)
        url = 'http://localhost:5000/Robonews/v1/predict'
        resp = requests.post(url, json=data)
        print(resp.text)

    except ConnectionError as err:
        print(err)
        return False
    except errors.DataProvidingException as err:
        print(err.message)
        return False
    except:
        print("Something Went Wrong!")
        return False


def main():
    predict_model(category='CryptoCurrency', pair='BTCUSDT', newsKeywords='bitcoin',
                  provider=['fxstreet'], concept_number=210,
                  resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                  )
    return


if __name__ == "__main__":
    main()
