# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 20:06:39 2020

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
from SentimentAnalysis.predictionModule import predict
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
        return urls
    except:
        print("Image URL reading Error!")
        return ' '


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
            json_output = BeautifulSoup(str(soup.find_all("script", id={"SeoApplicationJsonId"})), 'lxml')
            jsonText = json_output.get_text()
            jsonData = json.loads(jsonText, strict=False)
            for child in jsonData:
                description['articleBody'] = child['articleBody']
                description['keywords'] = child['keywords']
                # print( child['keywords'])
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
        description['articleBody'] = 'read article body error'
        description['keywords'] = 'read article body error'
        description['author'] = 'read article body error'
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
                for child in item:
                    if child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}pair':
                        news['pair'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}market':
                        news['market'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}TechAnalysis':
                        for c in child:
                            if c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}TrendIndex':
                                news['TrendIndex'] = c.attrib
                            elif c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}OBOSIndex':
                                news['OBOSIndex'] = c.attrib
                            elif c.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}PivotPoints':
                                news['PivotPoints'] = c.attrib

                        news['TechAnalysis'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}headline':
                        news['headline'] = child.text
                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}summary':
                        news['summary'] = child.text

                    elif child.tag == '{http://www.fxstreet.com/syndicate/rss/namespaces/}provider':
                        news['provider'] = child.text
                    else:
                        news[child.tag] = child.text
                querry = {'link': news['link']}

                exist = checkForExist1(querry)
                if not exist:

                    desc = getArticleBody(news['link'], 'articlebody.html')
                    for c in desc:
                        news[c] = desc[c]
                    news = JsonItemStandard(news)

                    saveInMongo1(news)
                    time.sleep(0.5)

                newsitems.append(news)

                # return news items list
        return newsitems
    except:
        print("Error in reading News")


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

        CryptoOtions = {'btcusd', 'bitcoin', 'cryptocurrency',
                        'ethusd', 'etherium', 'crypto', 'xpr',
                        'ripple', 'altcoin', 'crypto'}
        CommoditiesOptions = {'oil', 'gold', 'silver', 'wti', ',brent', 'commodities', 'xauusd', 'metals'}
        item = {}
        # print(item)
        item['title'] = newsItem['title']
        item['articleBody'] = newsItem['articleBody']
        # print(type( newsItem['pubDate']))
        # print( newsItem['pubDate'])
        currentDate = datetime.strptime(newsItem['pubDate'], '%a, %d %b %Y %H:%M:%S Z')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        # item['pubDate'] =  currentDateString
        # currentDate = datetime.strptime(newsItem['pubDate'], '%a, %d %b %Y %H:%M:%S Z')
        # currentDateString = currentDate.strftime('%a, %d %b %Y %H:%M:%S Z')
        # item['pubDate'] = currentDateString
        item['pubDate'] = int(currentDate.timestamp())

        item['keywords'] = newsItem['keywords']
        # print(newsItem['keywords'])
        item['author'] = newsItem['author']
        item['link'] = newsItem['link']
        item['provider'] = 'Fxstreet'
        if list(filter(lambda x: x.lower() in str(newsItem['keywords']), CryptoOtions)):
            item['category'] = 'Cryptocurrency'
        elif list(filter(lambda x: x.lower() in str(newsItem['keywords']), CommoditiesOptions)):
            item['category'] = 'Commodities'
        else:
            item['category'] = 'Forex'

        item['summary'] = newsItem['summary']
        item['thImage'] = newsItem['thImage']
        item['images'] = newsItem['images']
        #item['sentiment'], item['sentimentScore'], item['vector'] = predict(item)
        # item['PivotPoints'] = newsItem['PivotPoints']
        # item['TrendIndex'] = newsItem['TrendIndex']
        # item['OBOSIndex'] = newsItem['OBOSIndex']
        return item
    except:
        print("Error in standardization")


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


def fxstreetScraper():
    f = open('Forexlog.txt', 'a')
    url = 'http://xml.fxstreet.com/news/forex-news/index.xml'
    filename = 'topnewsfeed.xml'
    # load RSS File From Url
    now = datetime.now()
    print('crawling of fxstreet Started at ' + now.strftime('%a, %d %b %Y %H:%M:%S Z') + '!!')
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

    #exportForexCSV ()
    fxstreetScraper()
    return
if __name__ == "__main__":

    # calling mpai2n function 
    main()
