from datetime import datetime
from dataProvidingServices.dataProviding import prepairDataForLoad
from tensorflow.keras.models import load_model
import requests

SEQ_LEN = 7
marketDelayWindow = SEQ_LEN * 60 * 60
Training = True


def predict_model(category, pair):
    endDate = int(datetime.utcnow().timestamp())
    startDate = endDate - marketDelayWindow
    test_x, test_y, test_news_x, dates = prepairDataForLoad(category,
                                                            pair, startDate, endDate, Training=False)

    modelName = pair.upper() + 'WithNewsHourly.h5'
    model = load_model(modelName)

    pred_train = model.predict([test_x, test_news_x])
    data = {'category': category,
            'pair': pair,
            'timestamp': endDate,
            'predictedPrice': pred_train[-1]
            }
    url = 'http://localhost:5000/Robonews/v1/predict'
    resp = requests.post(url, json=data)
    print(resp.text)
