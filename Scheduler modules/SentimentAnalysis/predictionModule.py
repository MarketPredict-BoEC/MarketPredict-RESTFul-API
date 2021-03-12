"""
Created on Tue Sep  1 03:57:02 2020

@author: Novin
"""

import pickle
import numpy as np
from SentimentAnalysis.BoEC_WORD2VEC import testCaseProcess

'''
modelsPath
'''
EURUSDoptions = {'EURUSD', 'Euro'}
USDJPYoptions = {'USDJPY', 'Japan'}
BTCUSDoptions = {'BTCUSD', 'bitcoin', 'cryptocurrency'}
GBPUSDoptions = {'GBPUSD'}
ETHUSDoptions = {'ETHUSD', 'etherium', 'cryptocurrency'}
GOLDoptions = {'gold'}
OILoptions = {'oil'}


def modify(s):
    vec = s.replace('[', '')
    vec = vec.replace(']', '')
    vec = vec.split(',')
    vec = map(float, vec)
    vec = list(vec)
    return vec


def predict(newsItem):
    vec = testCaseProcess(newsItem)

    pair = ''
    # newsItem['keywords'] = [w.lower() for w in newsItem['keywords']]
    keywords = str(newsItem['keywords']).lower()
    if list(filter(lambda x: x in str(newsItem['keywords']), EURUSDoptions)):
        pair = 'EURUSD'
    if list(filter(lambda x: x in str(newsItem['keywords']), USDJPYoptions)):
        pair = 'USDJPY'
    if list(filter(lambda x: x in str(newsItem['keywords']), BTCUSDoptions)):
        pair = 'BTCUSD'
    '''
    if list( filter(lambda  x : x in str(newsItem['keywords']), GBPUSDoptions)):
            pair = 'GBPUSD'
    if list( filter(lambda  x : x in str(newsItem['keywords']), ETHUSDoptions)):
            pair = 'GBPUSD'
    if list( filter(lambda  x : x in str(newsItem['keywords']), GOLDoptions)):
            pair = 'GOLD'
    if list( filter(lambda  x : x in str(newsItem['keywords']), OILoptions)):
            pair = 'OIL'
    '''
    if len(pair) > 0:

        filename = str(pair) + 'finalized_model.sav'

        # load the model from disk
        loaded_model = pickle.load(open(filename, 'rb'))
        # print(vec)
        # only up or down predicyion based on change in close price by day timeframe

        vec2 = np.array(modify(vec)).reshape((1, -1))
        predict = loaded_model.predict(vec2)
        predict_prob = loaded_model.predict_proba(vec2)

        if (predict[0] == 0):
            predictValue = 'Negative'
        elif (predict[0] == 1):
            predictValue = 'Positive'
        return (predictValue, str(predict_prob[0]), vec)
    else:
        return ('Unkown', '0', '0')

