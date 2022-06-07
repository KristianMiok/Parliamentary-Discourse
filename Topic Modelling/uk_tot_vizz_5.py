# -*- coding: utf-8 -*-
"""UK Tot Vizz 5

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dCFZwxhye1sDX3iYYzn1A6KS1ZH9IXLA
"""

# To be run only once
if 0 == 1:
    !pip install gensim
    !pip install PyLDAvis
    !pip install spacy
    !python -m spacy download en_core_web_sm

# Access to resources
from google.colab import drive
drive.mount('/content/gdrive', force_remount=True)

# Read data from file
import pandas as pd
from sklearn.utils import shuffle

# Point to the file in Google Drive
# filename='/content/gdrive/My Drive/Topic Modeling/om.csv'
#filename='/content/gdrive/My Drive/EN_HS/big_dataset.csv'
df = pd.read_csv('/content/gdrive/My Drive/Text Summarization/UK/Data/total_80.txt', sep='\t',encoding="utf-8")

df.shape

df.columns

df['Speaker_role'].value_counts()

df1=df.loc[df['Speaker_type'] == "MP"]

df2=df1.loc[df1['Speaker_role'] == "Regular"]

df2.shape

papers=df2

# Cleaning!
# Load the regular expression library
import re

# Remove punctuation
papers['paper_text_processed'] = papers['V2'].map(lambda x: re.sub('[,\.!?]', '', x))

# Convert the titles to lowercase
papers['paper_text_processed'] = papers['paper_text_processed'].map(lambda x: x.lower())

# Print out the first rows of papers
papers['paper_text_processed'].head()

import gensim
from gensim.utils import simple_preprocess

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

data = papers.paper_text_processed.values.tolist()
data_words = list(sent_to_words(data))

print(data_words[:1][0][:30])

# Build the bigram and trigram models
bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100) # higher threshold fewer phrases.
trigram = gensim.models.Phrases(bigram[data_words], threshold=100)  

# Faster way to get a sentence clubbed as a trigram/bigram
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)

# NLTK Stop words
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = stopwords.words('english')
stop_words.extend(["say","time","want","know","friend","come","see","right","member","today","thing","may","year","week","put","last","make","leave","good","day","can","speak","great","place","thank","hear","must","way","go","think","debate","lord","member","question","plan","could","would","business","year",'people',"noble","say","government","lord","support","country","deal","work","pay","many","have", "give", "take", "make", "do", "get"])

# Define functions for stopwords, bigrams, trigrams and lemmatization
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB']):
    """https://spacy.io/api/annotation"""
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out

data_words_nostops = remove_stopwords(data_words)

type(data_words_nostops)

any("want" in w for w in data_words_nostops)

import spacy

# Remove Stop Words
data_words_nostops = remove_stopwords(data_words)

# Form Bigrams
data_words_bigrams = make_bigrams(data_words_nostops)

# Initialize spacy 'en' model, keeping only tagger component (for efficiency)
nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

# Do lemmatization keeping only noun, adj, vb, adv
data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB'])

print(data_lemmatized[:1][0][:30])

data_lemmatized2 = remove_stopwords(data_lemmatized)

print(len(stop_words))
print(len(data_lemmatized)-len(data_lemmatized2))

len(data_lemmatized2)

any("speak" in w for w in data_lemmatized)

import gensim.corpora as corpora

# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized2)

# Create Corpus
texts = data_lemmatized2

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# View
print(corpus[:1][0][:30])

# Build LDA model
lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                       id2word=id2word,
                                       num_topics=5, 
                                       random_state=100,
                                       chunksize=100,
                                       passes=10,
                                       per_word_topics=True)

print(lda_model)

!pip install pyLDAvis==2.1.2

import numpy as np
import tqdm
import pyLDAvis.gensim
import pickle 
import pyLDAvis
# Visualize the topics
pyLDAvis.enable_notebook()
LDAvis_prepared = pyLDAvis.gensim.prepare(lda_model, corpus, id2word,sort_topics=False)
LDAvis_prepared

from gensim.parsing.preprocessing import preprocess_string, strip_punctuation, strip_numeric

lda_topics = lda_model.show_topics(num_topics=5,num_words=30)
lda_topics
# topics = []
# filters = [lambda x: x.lower(), strip_punctuation, strip_numeric]

# for topic in lda_topics:
#     print(topic)
#     topics.append(preprocess_string(topic[1], filters))

pyLDAvis.save_html(LDAvis_prepared, '/content/gdrive/My Drive/Text Summarization/UK/Html/UK_tot5.html')