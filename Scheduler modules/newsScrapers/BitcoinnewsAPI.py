# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 12:09:25 2019

@author: Novin
"""
import requests
import json
from newsapi.newsapi_client import NewsApiClient
from datetime import datetime, timedelta
from  SentimentAnalysis.predictionModule import predict



def getCryptoNews(startDate, endDate):
    try:
        newsapi = NewsApiClient(api_key='caea8ad1719e40e0a08d563ae3405891')
        news = []
        bitcoin_articles = newsapi.get_everything(q='bitcoin',
                                                  sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                  domains='cnn,bloomberg,reuters,google',
                                                  from_param=startDate,
                                                  to=endDate,
                                                  language='en')
        BTC_articles = newsapi.get_everything(q='btc',
                                              sources='crypto-coins-news,bloomberg,reuters,google-news',
                                              domains='cnn,bloomberg,reuters,google',
                                              from_param=startDate,
                                              to=endDate,
                                              language='en')
        crypto_articles = newsapi.get_everything(q='cryptocurrency',
                                                 sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                 domains='cnn,bloomberg,reuters,google',
                                                 from_param=startDate,
                                                 to=endDate,
                                                 language='en')
        blockchain_articles = newsapi.get_everything(q='blockchain',
                                                     sources='crypto-coins-news,bloomberg,reuters,google-news',
                                                     domains='cnn,bloomberg,reuters,google',
                                                     from_param=startDate,
                                                     to=endDate,
                                                     language='en')

        for item in bitcoin_articles['articles']:
            news.append(item)

        for item in BTC_articles['articles']:
            news.append(item)

        for item in crypto_articles['articles']:
            news.append(item)
        for item in blockchain_articles['articles']:
            news.append(item)

    except:
        print('Error in Reading BTC News!')

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

    CryptoOtions = {'btcusd', 'bitcoin', 'cryptocurrency',
                    'ethusd', 'etherium', 'crypto', 'xpr',
                    'ripple', 'altcoin', 'crypto'}
    CommoditiesOptions = {'oil', 'gold', 'silver', 'wti', ',brent', 'commodities', 'xauusd', 'metals'}
    item = {}
    item['title'] = newsItem['title']
    item['articleBody'] = newsItem['description']
    currentDate = datetime.strptime(newsItem['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
    # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
    # print(currentDateString)
    item['pubDate'] = int(currentDate.timestamp())
    item['keywords'] = str(['bitcoin', 'btc', 'cryptocurrency'])
    item['author'] = newsItem['author']
    #item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
    item['link'] = newsItem['url']
    item['provider'] = newsItem['source']['name']
    item['summary '] = ''
    item['thImage'] = newsItem['urlToImage']
    item['category'] = 'Cryptocurrency'

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


def bitcoinNewsApi():
    endDate = datetime.today()
    startDate = datetime.today() - timedelta(days=29)
    # load RSS File From Url
    now = datetime.now()
    print('Crawling of Bitcoin News from API Started ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
    print('+---------------------------------------------+')
    newsitems = getCryptoNews(startDate, endDate)
    # store news items in a csv file
    saveInMongo1(newsitems)


'''
def main():
  bitcoinNewsApi()

if __name__ == "__main__":

    # calling mpai2n function 
    main()

'''




