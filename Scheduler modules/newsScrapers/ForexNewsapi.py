# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 12:09:25 2019

@author: Novin
"""
import json
import requests
from newsapi.newsapi_client import NewsApiClient

import pandas as pd
from datetime import datetime, timedelta
from SentimentAnalysis. predictionModule import predict
import time


def getForexNews(startDate, endDate):
    try:
        newsapi = NewsApiClient(api_key='caea8ad1719e40e0a08d563ae3405891')
        news = []
        eurusd_articles = newsapi.get_everything(q='eurusd',
                                                 sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                 domains='cnn,bloomberg,reuters,google',
                                                 from_param=startDate,
                                                 to=endDate,
                                                 language='en')
        usdjpy_articles = newsapi.get_everything(q='usdjpy',
                                                 sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                 domains='cnn,bloomberg,reuters,google',
                                                 from_param=startDate,
                                                 to=endDate,
                                                 language='en')

        forex_articles = newsapi.get_everything(q='forex',
                                                sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                domains='cnn,bloomberg,reuters,google',
                                                from_param=startDate,
                                                to=endDate,
                                                language='en')

        oil_articles = newsapi.get_everything(q='oil',
                                              sources='crypto-coins-news,bloomberg,reuters,google-news',
                                              domains='cnn,bloomberg,reuters,google',
                                              from_param=startDate,
                                              to=endDate,
                                              language='en')
        gold_articles = newsapi.get_everything(q='gold',
                                               sources='crypto-coins-news,bloomberg,reuters,google-news',
                                               domains='cnn,bloomberg,reuters,google',
                                               from_param=startDate,
                                               to=endDate,
                                               language='en')

        for item in forex_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'Forex'
            news.append(item)

        for item in eurusd_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'EURUSD'

            news.append(item)

        for item in usdjpy_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'USDJPY'

            news.append(item)
        for item in oil_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'oil'
            news.append(item)
        for item in gold_articles['articles']:
            item['provider'] = item['source']['name']
            item['keywords'] = 'gold'

        news.append(item)

    except:
        print('Error in Reading Forex2 News!,STATUS ERROR! 50 requests available every 12 hours')

    return (news)




def JsonItemStandard(newsItem):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : news provider
    # guid : Guid code
    # pair : explicitly tag by news provider and all the folllowing
    # indicator are based on this pair
    # pivotPoint : Pivot indicator at the time of news release time
    # trendIndex : Trend Index indicator at the news release time
    # ObosIndex : ObosIndex Indicator at the  news release time

    item = {}
    item['title'] = newsItem['title']
    item['articleBody'] = newsItem['description']
    print(newsItem['publishedAt'])
    # 2020-08-27T01:19:00Z
    currentDate = datetime.strptime(newsItem['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
    # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
    # print(currentDateString)
    item['pubDate'] = int(currentDate.timestamp())
    item['keywords'] = newsItem['keywords']
    item['author'] = newsItem['author']
    item['link'] = newsItem['url']
    item['provider'] = newsItem['provider']
    #item['sentiment'], item['sentimentScore'], item['vector'] =predict(item)
    item['thImage'] = newsItem['urlToImage']
    item['summary '] = ''

    return item


def saveInMongo1(newsItem):
    for item in newsItem:
        item = JsonItemStandard(item)
        querry = {'link': str(item['link'])}
        # mydoc = mycol.find(querry)
        exist = checkForExist1(querry)
        if not exist:
            # item = JsonItemStandard (item)
            url = 'http://localhost:5000/Robonews/v1/news'
            resp = requests.post(url, json=item)
            print(resp.text)

    print('+---------------------------------------------+')


def checkForExist1(query):
    url = 'http://localhost:5000/Robonews/v1/news'
    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    return resp['data']

def ForexNewsApi():
    endDate = datetime.today()
    startDate = datetime.today() - timedelta(days=29)
    # load RSS File From Url
    now = datetime.now()
    print('Crawling of Forex News from API Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
    print('+---------------------------------------------+')
    newsitems = getForexNews(startDate, endDate)
    # store news items in a csv file
    saveInMongo1(newsitems)



def main():
   ForexNewsApi()

if __name__ == "__main__":

    # calling mpai2n function 
    main()

