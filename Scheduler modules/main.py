import schedule
import time
import numpy as np
from datetime import datetime
from newsScrapers.FxstreetScraper import fxstreetScraper
from newsScrapers.FxstreetBitcoinScraper import fxstreetBitcoinScraper
from newsScrapers.InvestingCommoditiesFundamentalScraper import investingFundamentalScraper
from newsScrapers.InvestingCommooditiesTechnicalScraper import investingTechnicalScraper
from newsScrapers.BitcoinnewsAPI import bitcoinNewsApi
from newsScrapers.BitcoinnewsScraper import bitcoinNewsScrapper
from newsScrapers.conintelegraphScraper import cointelegraphScraper
from newsScrapers.ForexNewsapi import ForexNewsApi
from TrainingServices.modelTraining import train_model
from predictionServices.predictCurrencyPair import predict_model
import sys

sys.setrecursionlimit(1000)


def start():
    # load rss from web to update existing xml file
    print('started!!')
    print('+---------------------------------------------+')
    schedule.clear()
    schedule.every(60).minutes.do(fxstreetScraper)
    time.sleep(10)
    schedule.every(60).minutes.do(bitcoinNewsScrapper)
    time.sleep(10)
    schedule.every(60).minutes.do(fxstreetBitcoinScraper)
    time.sleep(10)
    schedule.every(60).minutes.do(cointelegraphScraper)
    time.sleep(10)
    schedule.every(60).minutes.do(investingTechnicalScraper)
    time.sleep(10)
    schedule.every(60).minutes.do(investingFundamentalScraper)
    time.sleep(10)
    schedule.every(420).minutes.do(bitcoinNewsApi)
    time.sleep(10)
    schedule.every(420).minutes.do(ForexNewsApi)
    time.sleep(10)

    # Training services scheduling
    job = train_model("forex", "EURUSD")
    i = "09:30"
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)

    # Training services scheduling
    job = train_model("forex", "USDJPY")
    i = "10:30"
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)

    job = train_model("forex", "GBPUSD")
    i = "11:30"
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)

    job = train_model("cryptocurrency", "BTCUSD")
    i = "12:30"
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)



    # PredictionServices scheduling

    schedule.every(1).hour.at(30).do(predict_model("forex", "EURUSD"))
    time.sleep(10)
    schedule.every(1).hour.at(30).do()
    time.sleep(10)
    schedule.every(1).hour.at(30).do()
    time.sleep(10)
    schedule.every(1).hour.at(30).do()
    time.sleep(10)

    hours = []
    for i in range(0,24):
        hours.append ( str(i)+'0:00')


    for i in hours:
        job =  predict_model("forex", "EURUSD")
        schedule.every().monday.at(i).do(job, i)
        schedule.every().tuesday.at(i).do(job, i)
        schedule.every().wednesday.at(i).do(job, i)
        schedule.every().thursday.at(i).do(job, i)
        schedule.every().friday.at(i).do(job, i)

        job = predict_model("forex", "USDJPY")
        schedule.every().monday.at(i).do(job, i)
        schedule.every().tuesday.at(i).do(job, i)
        schedule.every().wednesday.at(i).do(job, i)
        schedule.every().thursday.at(i).do(job, i)
        schedule.every().friday.at(i).do(job, i)

        job = predict_model("forex", "GBPUSD")
        schedule.every().monday.at(i).do(job, i)
        schedule.every().tuesday.at(i).do(job, i)
        schedule.every().wednesday.at(i).do(job, i)
        schedule.every().thursday.at(i).do(job, i)
        schedule.every().friday.at(i).do(job, i)

        job = predict_model("forex", "BTCUSD")
        schedule.every().monday.at(i).do(job, i)
        schedule.every().tuesday.at(i).do(job, i)
        schedule.every().wednesday.at(i).do(job, i)
        schedule.every().thursday.at(i).do(job, i)
        schedule.every().friday.at(i).do(job, i)


    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    start()


if __name__ == "__main__":
    # calling mpai2n function
    main()
