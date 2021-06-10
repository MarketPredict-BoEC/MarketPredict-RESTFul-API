from gensim.models import Word2Vec
import pathlib
import pandas as pd
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import re
from sklearn.cluster import KMeans
import numpy as np

#nltk.download('punkt')

# global variables
conceptNumbers = 210
topK = 0


def preprocess_text(sen):
    # Removing html tags
    sentence = remove_tags(sen)

    # Remove punctuations and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', sentence)

    # Single character removal
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)

    # Removing multiple spaces
    sentence = re.sub(r'\s+', ' ', sentence)

    return sentence


TAG_RE = re.compile(r'<[^>]+>')


# remove tags regular expression
def remove_tags(text):
    return TAG_RE.sub('', text)


# for preparing courpus we eliminate numbers and tags
def prepareCourpus(dataframe):
    # dataframe = pd.read_excel(corpusPath)
    totalCorpus = ''
    for item in dataframe.iterrows():
        text = item[1]['title'] + '.' + str(item[1]['articleBody'])
        sentences = sent_tokenize(text)
        preprocess_sent = [preprocess_text(sen) for sen in sentences]
        for item in preprocess_sent:
            totalCorpus = totalCorpus + item
    return totalCorpus


# for word2vec model we use Gensim library
def createW2VModel(dataframe, embeddingDim=210, windowSize=5):
    text = prepareCourpus(dataframe)
    vocabulary = word_tokenize(text)
    model = Word2Vec([vocabulary], size=embeddingDim, window=windowSize, min_count=3, workers=4)
    #model.save('forex.embeddings')
    #model.wv.save_word2vec_format('ForexNews.txt', binary=False)
    return model


def testCaseProcess(items,category , pair, conceptType):
    if conceptType =='total':
        current_Path = pathlib.Path().absolute()
        filePath = str(current_Path) + '/outputFiles/total/' + 'totalConcepts.xlsx'
    else:
        conceptFileName = category + pair + 'Concepts.xlsx'
        current_Path = pathlib.Path().absolute()
        filePath = str(current_Path) + '/outputFiles/' + category + '/' + pair + '/' + conceptFileName

    dfClusters = pd.read_excel(filePath)
    vectors = []
    for rowIndex, row in items.iterrows():
         vectors.append( BoEC_w2v(row, conceptNumbers, dfClusters, topK))

    return vectors


# create latent concept space
# conceptpath is the name of output file corresponding to concepts related to a currency pair
def conceptModeling(w2vModel, conceptNumbers):
    vectors = w2vModel.wv
    X = w2vModel[w2vModel.wv.vocab]
    kmeans_model = KMeans(conceptNumbers, init='k-means++', max_iter=100)
    Z = kmeans_model.fit(X)
    labels = kmeans_model.labels_.tolist()
    kmeans_model.fit_predict(X)
    words = list(w2vModel.wv.vocab)
    clusterWords = {'word': words, 'cluster': labels}
    clusterWordsData = pd.DataFrame(clusterWords)

    return clusterWordsData


def tokenize(text):
    text = preprocess_text(text)
    words = word_tokenize(text)
    return words


# create embedding vector for one news document
def BoEC_w2v(doc, conceptNumbers, clusters, topK):

    if doc['articleBody']:
        text = doc['title'] + doc['articleBody']
    else:
        text = doc['title']

    vec = pd.Series(np.zeros(conceptNumbers))
    words = tokenize(text)
    for word in words:
        vec[clusters[clusters['word'] == word]['cluster']] = vec[clusters[clusters['word'] == word]['cluster']] + 1
    if topK > 0:
        model = Word2Vec.load("forex.embeddings")
        expandVec = titleExpansion(doc['title'], topK, clusters, conceptNumbers, model)
        extende_vec = np.add(vec, expandVec)
    else:
        extende_vec = vec
    return extende_vec


# title expansion subroutine
def titleExpansion(docTitle, topK, clusters, conceptNumbers, w2vModel):
    expanded_words = tokenize(docTitle)
    vec = pd.Series(np.zeros(conceptNumbers))
    if topK == 0:
        return vec
    for word in expanded_words:
        if word in w2vModel.wv.vocab:
            synset = w2vModel.most_similar(word, topn=topK)

            for s in synset:
                vec[clusters[clusters['word'] == s[0]]['cluster']] = vec[clusters[clusters['word'] == s[0]][
                    'cluster']] + 1

    return vec


def createConcepts(dfDocuments, conceptNumbers=210, topK=0):
    w2vModel = createW2VModel(dfDocuments, embeddingDim=conceptNumbers, windowSize=3)
    clusterWordsData = conceptModeling(w2vModel, conceptNumbers)
    return clusterWordsData


# BoEC-word2vec create embedded document vectors for all of news in corpus
def BoEC_word2vec(dfDocuments, outputFileName, conceptNumbers, topK=0, embeddingDim=100, windowSize=3):
    w2vModel = createW2VModel(dfDocuments, embeddingDim=210, windowSize=3)
    conceptModeling(w2vModel, conceptNumbers, 'topicInfo.xlsx')
    dfClusters = pd.read_excel('topicInfo.xlsx')
    # dfDocuments = pd.read_excel(corpusPath)
    df = pd.Series(np.zeros(dfDocuments['title'].count()))

    for rowIndex, row in dfDocuments.iterrows():
        # text = str(row[''])
        vec = BoEC_w2v(row, conceptNumbers, dfClusters, topK)
        df[rowIndex] = str([w for w in vec])

    dfDocuments['vector'] = df
    dfDocuments.to_excel(outputFileName)
    return dfDocuments


'''    

def main():


    corpusPath = 'testCase.xlsx'
    outputFileName  = 'outputTestCase.xlsx'
    df = BoEC_word2vec(corpusPath , outputFileName ,
                  conceptNumbers = 10 ,topK = 0 )
    exportSubNews.exportNews('BTCUSD',{'bitcoin'},df)

    return

if __name__ == "__main__":

    # calling mpai2n function 
    main()   
'''
