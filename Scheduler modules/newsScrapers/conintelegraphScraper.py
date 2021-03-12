# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020
Crawl cryptocurrencies news from cointelegraph.
I use rss of all coins news
@author: Novin
"""

# Python code to illustrate parsing of XML files  from fxstreet xml provider
# importing the required modules


import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import pandas as pd
# from flask import Flask
# from flask import request, jsonify
from datetime import datetime
from SentimentAnalysis. predictionModule import predict
import time


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
    try:

        soup = BeautifulSoup(content, 'html.parser')
        img_tags = soup.find_all('img', src=True)

        urls = [img['src'] for img in img_tags]
        return urls[0]
    except:
        print("Image URL Reed Error!")
        return -1


def getArticleBody(url, filename):
    loadPage(url, filename)
    f1 = open('nonScrapedLink.txt', 'a')
    try:

        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        description = {}
        if content != 'fail':
            soup = BeautifulSoup(content, 'html.parser')
            json_output = BeautifulSoup(str(soup.find_all
                                            (lambda tag: tag.name == 'div' and tag.get('class')
                                                         == ['post-content'])), "lxml")

            jsonText = json_output.get_text()
            description = str(jsonText)
        else:
            f1.write(url)
            f1.write('\n')
            f1.close()

    except  json.JSONDecodeError as err:
        print('read article body error: ', err)

    return (description)


def parseXML(xmlfile):
    try:
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        root = tree.getroot()
        # create empty list for news items
        newsitems = []
        # iterate news items
        for item in root:

            for item in item.findall('item'):
                news = {}
                category = {}
                for child in item:
                    if child.tag == '{http://purl.org/dc/elements/1.1/}creator':
                        news['author'] = child.text.replace('Cointelegraph By ', '')
                    elif child.tag == 'category':
                        category['item{}'.format(len(category) + 1)] = child.text
                    elif child.tag == 'description':
                        news['thImage'] = getImageURL(child.text)
                        news['summary'] = child.text


                    else:
                        news[child.tag] = child.text
                news['category'] = category
                querry = {'link': news['link']}

                exist = checkForExist1(querry)
                if not exist:
                    news['articleBody'] = getArticleBody(news['link'], 'articlebody.html')
                    #print(news)
                    news = JsonItemStandard(news)

                    saveInMongo1(news)
                    time.sleep(0.5)

                newsitems.append(news)

                # return news items list
        return newsitems
    except:
        print("Read XML Error!")
        return -1


def JsonItemStandard(newsItem):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider
    # sentiment : predictionServices positive/negative
    # predict : predictionServices probability

    try:

        item = {}

        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['articleBody']
        currentDate = datetime.strptime(newsItem['pubDate'], '%a, %d %b %Y %H:%M:%S +0000')
        item['pubDate'] = int(currentDate.timestamp())
        item['keywords'] = list(newsItem['category'].values())
        # item['keywords'] = keywords
        item['author'] = newsItem['author']
        item['link'] = newsItem['link']
        item['provider'] = 'cointelegraph'
        item['category'] = 'Cryptocurrency'
        # todo : check for summary
        item['summary'] = ''
        item['thImage'] = newsItem['thImage']
        item['images'] = ''
        #item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
        return item
    except:
        print("Standardization ERROR!")



def checkForExist1(query):
    url = 'http://localhost:5000/Robonews/v1/news'
    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    return resp['data']


def saveInMongo1(item):
    url = 'http://localhost:5000/Robonews/v1/news'
    resp = requests.post(url, json=item)
    print(resp.text)
    # todo : exception handling
    return


def cointelegraphScraper():
    f = open('Forexlog.txt', 'a')
    url = 'https://cointelegraph.com/rss'

    filename = 'topnewsfeed.xml'
    # load RSS File From Url
    now = datetime.now()
    print('crawling of cointelegraph Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S') + '!!')
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


    cointelegraphScraper()
    return
if __name__ == "__main__":

    # calling mpai2n function 
    main()
