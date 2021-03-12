# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020

@author: Novin
"""

# Python code to illustrate directly parsing the news page with beautifulsoap python package

# importing the required modules

import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from SentimentAnalysis.predictionModule import predict


def loadPage(url, fileName=None):
    # url of rss feed
    try:
        # creating HTTP response object from given url
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        resp = requests.get(url, timeout=3, headers=headers)
        fail = 'fail'
        if resp.status_code == 200:
            # saving the xml file
            with open(fileName, 'wb') as f:
                f.write(resp.content)
                f.close()
                return 1
        else:
            with open(fileName, 'wb') as f:
                f.write(bytes(fail.encode()))
                f.close()

                return -1

        resp.close()
        resp.raise_for_status()

    except requests.exceptions.HTTPError as htError:
        print('Http Error: ', htError)

    except requests.exceptions.ConnectionError as coError:
        print('Connection Error: ', coError)
    except requests.exceptions.Timeout as timeOutError:
        print('TimeOut Error: ', timeOutError)
    except requests.exceptions.RequestException as ReError:
        print('Something was wrong: ', ReError)
    return (-1)


def getImageURL(content):
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img', src=True)

    urls = [img['src'] for img in img_tags]
    return urls


def getArticleBody(url, filename='None'):
    loadPage(url, filename)
    f1 = open('nonScrapedLink.txt', 'a')
    try:

        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        description = {}
        if content != 'fail':

            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all("script", id={"SeoApplicationJsonId"})), 'lxml')
            jsonText = json_output.get_text()
            jsonData = json.loads(jsonText, strict=False)
            for child in jsonData:
                if type(child['articleBody']) != type(''):
                    description['articleBody'] = child['articleBody']
                else:
                    description['articleBody'] = ''
                description['keywords'] = child['keywords']
                if len(child['image']) > 0:
                    description['thImage'] = child['image'][0]
                else:
                    description['thImage'] = ''
                description['author'] = child['author']['name']

                description['images'] = getImageURL(content)
        else:
            f1.write(url)
            f1.write('\n')
            f1.close()

    except  json.JSONDecodeError as err:
        print('read article body error: ', err)
    return (description)


def parseXML(filename):
    f = open(filename, 'r', encoding='utf-8')
    content = f.read()
    description = []
    if content != 'fail':

        soup = BeautifulSoup(content, 'html.parser')
        json_output = BeautifulSoup(str(soup.find_all("script", type={"application/ld+json"})), 'lxml')
        #print(json_output)

        jsonText = json_output.text
        #print(jsonText)
        jsonData = json.loads(jsonText, strict=False)
        for child in jsonData:
            newEntry = dict()
            if 'datePublished' in child:

                newEntry['title'] = child['headline']
                newEntry['pubDate'] = child['datePublished']
                newEntry['link'] = child['url']
                newEntry['author'] = child['author']['name']

                other = getArticleBody(child['url'], 'item.html')

                for c in other:
                    newEntry[c] = other[c]
                newEntry['pubDate'] = child['datePublished']
                # print(newEntry)
                saveInMongo1(newEntry)

    # return news items list
    return description




def checkForExist1(query):
    url = 'http://localhost:5000/Robonews/v1/news'
    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    return resp['data']


def saveInMongo1(item):
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # mydb = myclient["new_EconomicNewsDataBase"]
    # mycol = mydb["ROBONEWSCOLLECTION"]
    querry = {'link': str(item['link'])}
    exist = checkForExist1(querry)
    # print(item)
    if not exist:
        item = JsonItemStandard(item)
        # print(item)
        url = 'http://localhost:5000/Robonews/v1/news'
        resp = requests.post(url, json=item)
        print(resp.text)


def JsonItemStandard(newsItem):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider
    CryptoOtions = {'btcusd', 'bitcoin', 'cryptocurrency',
                    'ethusd', 'etherium', 'crypto', 'xpr',
                    'ripple', 'altcoin', 'crypto'}
    CommoditiesOptions = {'oil', 'gold', 'silver', 'wti', ',brent', 'commodities', 'xauusd', 'metals'}
    item = {}
    item['title'] = newsItem['title']
    item['articleBody'] = newsItem['articleBody']
    currentDate = datetime.strptime(newsItem['pubDate'], '%m/%d/%Y %I:%M:%S %p')
    item['pubDate'] = int(currentDate.timestamp())
    # keywords = [w.lower() for w in newsItem['keywords']]
    item['keywords'] = newsItem['keywords']
    # item['keywords'] = keywords
    item['author'] = newsItem['author']
    item['link'] = newsItem['link']
    item['provider'] = 'FXstreet CryptoCurrency'
    #item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
    item['summary'] = ''
    item['thImage'] = newsItem['thImage']
    item['images'] = newsItem['images']
    if list(filter(lambda x: x.lower() in str(newsItem['keywords']), CryptoOtions)):
        item['category'] = 'Cryptocurrency'
    elif list(filter(lambda x: x.lower() in str(newsItem['keywords']), CommoditiesOptions)):
        item['category'] = 'Commodities'
    else:
        item['category'] = 'Forex'

    return item


def fxstreetBitcoinScraper():
    f = open('Forexlog.txt', 'a')
    url = 'https://www.fxstreet.com/cryptocurrencies/news'
    filename = 'topnewsfeed.html'
    # load RSS File From Url
    now = datetime.now()
    print('crawling of fxstreet for Crypocurrencies Started ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
    print('+---------------------------------------------+')
    code = loadPage(url, filename)
    if code == 1:
        parseXML(filename)
        print('+---------------------------------------------+')
    # store news items in a csv file
    else:
        f.write('Connection Error at time : ' + datetime.now().strftime('%y %m %d %H %M %S') + '\n')
        f.close()



def main():
    fxstreetBitcoinScraper()

if __name__ == "__main__":

    # calling mpai2n function 
    main()

