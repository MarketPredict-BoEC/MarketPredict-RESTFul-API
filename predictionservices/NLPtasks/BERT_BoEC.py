# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 08:48:22 2020
@author: Novin
"""
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from BERT_vectorization import getEmbedding
from nltk.tokenize import word_tokenize
import re
import requests
import json

def createConcepts(output_dict, NUM_CLUSTERS,pair):
    X = []
    words = []
    articles = []

    for item in output_dict:
        if item != None:
            X.append(item['vector'])
            words.append(item['key'])
            articles.append(item['articleID'])

    # fit the model

    kmeans_model = KMeans(NUM_CLUSTERS, init='k-means++', max_iter=100)
    Z = kmeans_model.fit(X)
    labels = kmeans_model.labels_.tolist()
    clusterWords = {'word': words, 'cluster': labels, 'vector': X, 'article_ID': articles}

    # write to file
    clusterWordsData = pd.DataFrame(clusterWords)
    filename = 'topicInfo.xlsx'

    clusterWordsData.to_excel(filename)

    clusterWordsData['pair'] = pair
    url = 'http://localhost:5000/Robonews/v1/concepts'

    query = {'keywords': pair,

             }

    resp = requests.post(url, data=clusterWordsData)
    return (clusterWordsData)


def readVector(text):
    vec = []
    text = text.replace('[', '')
    text = text.split(' ')
    for v in text:
        if v != '':
            vec.append(float(v))
    return vec


def readEmbedding(text, articleID):
    output = {'key': '', 'vector': [], 'articleID': ''}

    if len(text) > 1:
        text = text.split('\t')
        output['key'] = text[0].replace('\n', '')
        output['articleID'] = articleID
        output['vector'] = readVector(text[1])
    return (output)


def get_embeddings(dataframe):
    dataframe = getEmbedding(dataframe)
    embeddings = dataframe['embedding']
    i = 0
    for text in embeddings:
        text = text.replace('[CLS]', '#CLS#')
        text = text.replace('[SEP]', '#SEP#')
        lines = text.split(']')
        for line in lines:
            output = readEmbedding(line,dataframe.iloc[ i,'articleID'])
            if output['key'] != '':
                embeddings.append(output)
        i = i+1
    return (embeddings)


def vectorization(name, data, NUM_CLUSTERS):
    output = {'articleID': 0, 'words': [], 'vector': []}
    output['articleID'] = name
    vector = np.zeros(NUM_CLUSTERS)
    output['words'] = [w for w in data['word']]
    for item in data['cluster']:
        vector[item] = vector[item] + 1
    output['vector'] = vector
    return output


def getAppendTopsimilar(group, topK):
    data = group[1]
    index = np.argsort(data['simScore'])
    clusters = [data['simScore'].iloc[v] for v in index]
    return clusters


def vectorize(data, topK, clusterNum):
    groups = data.groupby('targetKey')
    vec = np.zeros(clusterNum)
    for group in groups.iterrows():
        exAppendVec = getAppendTopsimilar(group, topK)
        for i in exAppendVec:
            vec[i] = vec[i] + 1
    return vec




def BoEC_bert(dataframe, NUM_CLUSTERS=210, topN=7):
    data_output = []
    vectors = []

    # BERT embedding of text
    outputData = get_embeddings(dataframe)

    # latent concept modeling
    clusterd_data = createConcepts(outputData, NUM_CLUSTERS)

    # document vectorization process
    groups = clusterd_data.groupby(['article_ID'])
    for name, group in groups:
        data_output.append(vectorization(name, group, NUM_CLUSTERS))
    df = pd.DataFrame(data=data_output, columns=['articleID', 'words', 'vector'])


    # add vector for both title, content and title expansion
    for rowindex, row in df.iterrows():
        # DISTIBERT sentimentScore
        vec1 = row['senScore']
        vec2 = row['vector']
        vectors.append( vec2,[vec1])
    df['extended vector'] = vectors
    df.to_excel('BERT content Vectorization.xlsx')
    return df

def tokenize(text):
    text = preprocess_text(text)
    words = word_tokenize(text)
    return words
# remove tags regular expression

def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)

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

# in test set we did for vectorization
def testCaseVectorization(item,pair,NUM_CLUSTERS=210,):
    if item['articleBody']:
        text = item['title'] + item['articleBody']
    else:
        text = item['title']

    vec = pd.Series(np.zeros (NUM_CLUSTERS))
    url = 'http://localhost:5000/Robonews/v1/concepts'

    query = {'keywords': pair,

             }

    resp = requests.get(url, params=query)
    resp = json.loads(resp.text)
    data = json.loads(resp['data'])
    clusters = pd.DataFrame(data)

    words = tokenize(text)
    for word in words:
        vec[clusters[clusters['word'] == word]['cluster']] = vec[clusters[clusters['word'] == word]['cluster']] + 1
    vec1 = item['senScore']
    return np.concatenate((vec,[vec1]))




