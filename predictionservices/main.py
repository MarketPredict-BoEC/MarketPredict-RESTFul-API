from ConceptModeling.conceptModeling import prepaireConcepts
from trainingServices.modelTraining import train_model
from predictionServices.predictCurrencyPair import predict_model
import schedule
import time
from datetime import datetime
import pandas as pd


def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))


def firstUsage():
    support = {
        'Forex': ['EURUSD', 'USDJPY', "GBPUSD", 'XAUUSD'],
        'CryptoCurrency': ['BTCUSDT'],
    }
    try:
        #prepaireConcepts(category='Cryptocurrency', pair='BTCUSDT', keywords='bitcoin')

        # prepaireConcepts(category='Forex', pair='EURUSD', keywords='EURUSD')
        # prepaireConcepts(category='Forex', pair='USDJPY', keywords='USDJPY')
        # prepaireConcepts(category='Forex', pair='GBPUSD', keywords='GBPUSD')
        # prepaireConcepts(category='Forex', pair='USDCHF', keywords='USDCHF')
        # prepaireConcepts(category='Forex', pair='XAUUSD', keywords='gold')
        '''
        # ____________Model Training____________________ #
        train_model(category='Forex', pair='USDJPY', newsKeywords='USDJPY',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=150, learningRate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='EURUSD', newsKeywords='EURUSD',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=150, learningRate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='GBPUSD', newsKeywords='GBPUSD',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=150, learningRate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='USDCHF', newsKeywords='USDCHF',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=150, learningRate=0.001, decay=1e-6, batch_size=32)

        train_model(category='Forex', pair='USDCHF', newsKeywords='USDCHF',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=150, learningRate=0.001, decay=1e-6, batch_size=32)
        train_model(category='Forex', pair='XAUUSD', newsKeywords='gold',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                    epoch=300, learningRate=0.5, decay=1e-3, batch_size=32)
        '''
        train_model(category='Cryptocurrency', pair='BTCUSDT', newsKeywords='bitcoin',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                        epoch=300, learningRate=0.5, decay=1e-3, batch_size=32)



    except:
        print("Something went wrong!")
        return False


def predictionBussinessDay():
    try:
        time.sleep(2)
        predict_model(category='Forex', pair='EURUSD', newsKeywords='EURUSD',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )
        time.sleep(2)
        predict_model(category='Forex', pair='USDJPY', newsKeywords='USDJPY',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )
        time.sleep(2)
        predict_model(category='Forex', pair='GBPUSD', newsKeywords='GBPUSD',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )
        time.sleep(2)
        predict_model(category='Forex', pair='USDCHF', newsKeywords='USDCHF',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )
        time.sleep(2)

        predict_model(category='Forex', pair='XAUUSD', newsKeywords='gold',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )
        return True
    except:
        print("Unknown Error")
        return False


def predictionFullTimeMarket():
    try:
        time.sleep(2)
        predict_model(category='CryptoCurrency', pair='BTCUSDT', newsKeywords='bitcoin',
                      provider=['fxstreet'], concept_number=210,
                      resolution=60, SEQ_LEN_news=7, SEQ_LEN=7, max_L=15, conceptsType='pair',
                      )

    except:
        print("Unknown Error")
        return False


def predictionServices():
    try:
        utcNow = datetime.utcnow()
        if is_business_day(utcNow):
            predictionBussinessDay()
        predictionFullTimeMarket()
    except:
        print("Unknown Error")
        return False


def trainingBussinessDay():
    try:
        train_model(category='Forex', pair='EURUSD',
                    newsKeywords='EURUSD',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='USDJPY',
                    newsKeywords='USDJPY',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='GBPUSD',
                    newsKeywords='GBPUSD',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='USDCHF',
                    newsKeywords='USDCHF',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )
        train_model(category='Forex', pair='XAUUSD',
                    newsKeywords='gold',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )

    except:
        return False


def trainingFullTimeMarkets():
    try:
        train_model(category='CryptoCurrency', pair='BTCUSDT',
                    newsKeywords='bitcoin',
                    provider=['fxstreet'], concept_number=210,
                    resolution=60, SEQ_LEN_news=7,
                    SEQ_LEN=7, max_L=15, conceptsType='pair'
                    , epoch=60, learningRate=0.001, decay=1e-6, batch_size=32
                    )
    except:
        return False


def trainingServices():
    try:
        utcNow = datetime.utcnow()
        if is_business_day(utcNow):
            trainingBussinessDay()
        trainingFullTimeMarkets()
    except:
        print("Unknown Error")
        return False


def conceptModeling():
    try:
        prepaireConcepts(category='Forex', pair='EURUSD')
        prepaireConcepts(category='Forex', pair='USDJPY')
        prepaireConcepts(category='Forex', pair='GBPUSD')
        prepaireConcepts(category='Forex', pair='USDCHF')
        prepaireConcepts(category='Cryptocurrency', pair='bitcoin')
        prepaireConcepts(category='Forex', pair='gold')
    except:
        print("Concept Modeling Failed")
        return False


def start():
    print('started!!')
    print('+---------------------------------------------+')
    schedule.clear()

    # Concept modeling scheduling
    # We update our concepts every month
    schedule.every(30).days.do(prepaireConcepts)
    # Model Training Scheduling
    # We update our concepts every month
    schedule.every(24).hours.do(trainingServices)

    schedule.every(1).minutes.do(predictionServices)

    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    #firstUsage()
    start()


if __name__ == "__main__":
    # calling mpai2n function
    main()
