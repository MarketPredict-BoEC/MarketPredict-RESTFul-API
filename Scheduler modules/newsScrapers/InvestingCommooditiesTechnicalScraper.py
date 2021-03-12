# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 06:32:42 2021

@author: Novin
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 07:21:47 2021

@author: Novin
"""

# Python code to illustrate parsing of XML files  from fxstreet xml provider
# importing the required modules


import requests
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from SentimentAnalysis. predictionModule import predict
import re


def cleanText(sen):
    # lowercase
    sen = sen.lower()
    # remove tag
    sentence = re.sub(r'<[^>]+>', ' ', sen)
    # remove url from sentence
    sentence = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|-)*\b',
                      '', sen)
    # Remove punctuations and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', sentence)
    # Single character removal
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)
    # Removing multiple spaces
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


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


def getArticleBody(url, filename):
    loadPage(url, filename)
    f1 = open('nonScrapedLink.txt', 'a')
    try:

        description = {}
        f = open(filename, 'r', encoding='utf-8')
        content = f.read()
        description = {}
        if content != 'fail':

            soup = BeautifulSoup(content, 'html.parser')
            result = soup.findAll(attrs={'class': re.compile(r"^WYSIWYG articlePage$")})
            jsonText = ''
            articlebody = ''
            for ele in result:
                # print(ele)
                articlebody += ele.get_text()
                jsonText += ele.get_text()
            description['articleBody'] = str(articlebody)
            description['images'] = getImageURL(content)

        else:
            f1.write(url)
            f1.write('\n')
            f1.close()

    except  json.JSONDecodeError as err:
        print('read article body error: ', err)
        description['articleBody'] = 'read article body error'
        description['images'] = 'read image error'
    return (description)


def parseXML(xmlfile):
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
            for child in item:

                if child.tag == 'enclosure':
                    news['link'] = child.attrib['url']
                news[child.tag] = child.text
            querry = {'link': news['link']}

            exist = checkForExist1(querry)
            if not exist:

                desc = getArticleBody(news['link'], 'articlebody.html')
                for c in desc:
                    news[c] = desc[c]
                news = JsonItemStandard(news)
                saveInMongo1(news)
            newsitems.append(news)

            # return news items list
    return newsitems


def JsonItemStandard(newsItem):
    # title : News Headline
    # articleBody : News content
    # pubDate : news timestamp
    # keywords : news keywords
    # author : author of news
    # url : url
    # summary : Breif summary about news
    # provider : provider

    goldCommoditiesOptions = ['gold', 'xauusd']
    oilCommoditiesOptions = ['oil', 'brent', 'wti']
    silverCommoditiesOptions = ['silver', 'xagusd']
    copperCommoditiesOptions = ['copper']
    gasCommoditiesOptions = ['gas']
    item = {}
    # print(item)
    item['title'] = newsItem['title']
    item['articleBody'] = newsItem['articleBody']
    currentDate = datetime.strptime(newsItem['pubDate'], '%b %d, %Y %H:%M GMT')
    # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
    item['pubDate'] = int(currentDate.timestamp())

    item['author'] = newsItem['author']
    item['link'] = newsItem['link']
    item['provider'] = 'Investing'
    item['category'] = 'Commodities'
    item['summary'] = ''
    item['thImage'] = ''
    #  Manual keywords initialization
    item['keywords'] = ''
    sw = 0
    for val in goldCommoditiesOptions:
        if val in newsItem['title'].lower().split():
            item['keywords'] = str(goldCommoditiesOptions).lstrip('[').rstrip(']')
            sw = 1
            break
    if not sw:
        for val in oilCommoditiesOptions:
            if val in newsItem['title'].lower().split():
                item['keywords'] = str(oilCommoditiesOptions).lstrip('[').rstrip(']')
                break
    if not sw:

        for val in silverCommoditiesOptions:
            if val in newsItem['title'].lower().split():
                item['keywords'] = str(silverCommoditiesOptions).lstrip('[').rstrip(']')
                sw = 1
                break
    if not sw:
        for val in copperCommoditiesOptions:
            if val in newsItem['title'].lower().split():
                item['keywords'] = str(copperCommoditiesOptions).lstrip('[').rstrip(']')
                sw = 1
                break
    if not sw:
        for val in gasCommoditiesOptions:
            if val in newsItem['title'].lower().split():
                item['keywords'] = str(gasCommoditiesOptions).lstrip('[').rstrip(']')
                sw = 1
                break
    item['images'] = newsItem['images']
    item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
    return item


def getImageURL(content):
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img', src=True)

    urls = [img['src'] for img in img_tags]
    return urls


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

def investingTechnicalScraper():
    f = open('Forexlog.txt', 'a')
    url = 'https://www.investing.com/rss/commodities_Technical.rss'
    filename = 'topnewsfeed.xml'
    # load RSS File From Url
    now = datetime.now()
    print('crawling of Investing for Forex Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
    print('+---------------------------------------------+')
    code = loadPage(url, filename)
    if code == 1:
        parseXML(filename)
        print('+---------------------------------------------+')
    # store news items in a csv file
    else:
        f.write('Connection Error at time : ' + datetime.now().strftime('%y %m %d %H %M %S') + '\n')
        f.close()


'''

def main():

    #exportForexCSV ()
    InvestingScraper()
    return
if __name__ == "__main__":

    # calling mpai2n function 
    main()
'''