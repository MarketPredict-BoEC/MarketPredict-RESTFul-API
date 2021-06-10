from NLPtasks.BERT_BoEC import createConcepts
import requests
import json
import pandas as pd
import pathlib, sys


def saveConcepts(concepts, category='', pair='', total=False):
    if total:
        #todo : add current path to path variable
        current_Path = pathlib.Path().absolute()
        path = str(current_Path)+'/outputFiles/total'
        filePath = (current_Path)+ '/outputFiles/total/' + 'totalConcepts.xlsx'
    else:
        conceptFileName = category + pair + 'Concepts.xlsx'
        current_Path = pathlib.Path().absolute()
        path = str(current_Path)+'/outputFiles/' + category + '/' + pair
        filePath = str(current_Path)+'/outputFiles/' + category + '/' + pair + '/' + conceptFileName
        print(filePath)


    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    concepts.to_excel(filePath)


def prepaireConcepts(category='', pair='', keywords='',total=False, conceptNumber=210):
    try:
        print('-------------Start Concept MOdeling--------------------------')
        dfDocument = prepairNews(category, keywords, total)
        print('Pair: {}'.format(pair))
        print('Total News Document: {}'.format(len(dfDocument)))
        concepts = createConcepts(dfDocument, conceptNumber)
        if total:

            saveConcepts(concepts, total=True)
        else:

            saveConcepts(concepts, category=category, pair=pair)
        print('-------------successfully completed!--------------------------')
        return
    except:
        print("Unexpected error:", sys.exc_info()[0])


def prepairNews(category='', pair='', total=False):
    try:
        url = 'http://localhost:5000/Robonews/v1/news'
        if not total:
            parameters = {
                'category': category,
                'keywords': pair
            }
        else:
            parameters = {
                'category': 'all'
            }
        reps = requests.get(url, params=parameters)
        if reps.status_code == 200:
            data = json.loads(reps.text)
            data = json.loads(data['data'])
            if data is None:
                raise Exception('No news for target currency pair {}'.format(pair))
            dfDocuments = pd.DataFrame(data=data)
            return dfDocuments
    except:
        print("Error in news preparation!")
    return None



def main():
    prepaireConcepts(category='Cryptocurrency',pair='bitcoin')
    return


if __name__ == "__main__":
    main()

