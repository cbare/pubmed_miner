import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import re
import requests
import seaborn as sns; sns.set()
import sys
from argparse import Namespace
from collections import Counter, namedtuple
from lxml import etree
from tqdm import tqdm

import gensim
from gensim import corpora
from gensim import models
from gensim import utils
from gensim.parsing.preprocessing import preprocess_string
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamodel import LdaModel


## build a context-specific set of stopwords
medical_stopwords = {'patient', 'patients', 'clinical', 'treatment', 'disease',
                     'present', 'new', 'diagnosis', 'disorder', 'disorders', 'associated'}
STOPWORDS = gensim.parsing.preprocessing.STOPWORDS | medical_stopwords



def remove_stopwords(s):
    s = utils.to_unicode(s)
    return " ".join(w for w in s.split() if w not in STOPWORDS)


def custom_preprocess(s):
    """
    Modify gesim's default set of filters to include our extra stopwords
    """
    filters = [
        lambda x: x.lower(),
        gensim.parsing.preprocessing.strip_punctuation,
        gensim.parsing.preprocessing.strip_multiple_whitespaces,
        gensim.parsing.preprocessing.strip_numeric,
        remove_stopwords,
        gensim.parsing.preprocessing.stem_text
    ]
    return preprocess_string(s, filters=filters)


def fit(n_topics, min_occur, iterations, passes, texts, wc):
    """
    Fit an LDA model of n topics to texts.
    """
    bigrams = models.Phrases(texts, min_count=3)
    trigrams = models.Phrases(bigrams[texts], min_count=3)

    texts = [[w for w in t if (len(w)>1 and wc[w]>min_occur)] for t in texts]

    texts = [text + [x for x in bigrams[text] if '_' in x]
                  + [x for x in trigrams[text] if '_' in x]
             for text in texts]

    dictionary = corpora.Dictionary(texts)
    bows = [dictionary.doc2bow(text) for text in texts]

    lda = LdaModel(bows, id2word=dictionary, num_topics=n_topics,
                   alpha='auto', eta='auto',
                   iterations=iterations,
                   passes=passes,
                   eval_every=1)

    coherence_model_lda = CoherenceModel(model=lda,
                                     texts=texts,
                                     dictionary=dictionary,
                                     coherence='c_v')
    coherence = coherence_model_lda.get_coherence()

    return Namespace(**locals())


def bows_to_matrix(bows):
    """
    Convert list of bag-of-words in sparse format to matrix format.

    Todo: return a sparse format from scipy.sparse instead of dense matrix.
    """
    X = np.zeros((len(best.bows),len(best.dictionary)))
    for i, bow in enumerate(best.bows):
        for j, x in bow:
            X[i,j] = x
    return X


def score(true_labels, predicted_labels):
    """
    Compute sklearn's metrics on a clustering
    """
    results = {
        'homogeneity': metrics.homogeneity_score(true_labels, predicted_labels),
        'completeness': metrics.completeness_score(true_labels, predicted_labels),
        'v_measure': metrics.v_measure_score(true_labels, predicted_labels),
        'adjusted_rand_score': metrics.adjusted_rand_score(true_labels, predicted_labels),
    }


def silhouette_score(X, predicted_labels, sample_size=1000):
    return metrics.silhouette_score(X, predicted_labels, sample_size=sample_size)


def find_best_model(results):
    """
    Select the model with the highest coherence score
    """
    max_coherence = 0.0
    max_index = None
    for j,(m,i,p,fo) in enumerate(results):
        if fo.coherence > max_coherence:
            max_index = j
            max_coherence = fo.coherence
    return results[max_index]


def max_i(a):
    return max(a, key=lambda x: x[1])[0]


def noop(a):
    return a


def print_result(pubmed_ids, result, discretize, out=None):
    """
    Output results to out file in a two column tab-separated format
    """
    if discretize:
        f = max_i
    else:
        f = noop

    if not out:
        out = sys.stdout
    for pmid, bow in zip(pubmed_ids, result.bows):
        print('\t'.join((pmid, f(result.lda.get_document_topics(bow)))), file=out)


def cluster(articles, params, best_of_n=None):
    texts = [custom_preprocess(a.title + ' ' + a.abstract) for a in articles]
    wc = Counter(w for t in texts for w in t)
    k, m, i, p = (params[key] for key in ['k', 'min_occur', 'iterations', 'passes'])

    if best_of_n:
        results = [(m, i, p, fit(k, m, i, p, texts, wc)) for _ in tqdm(range(best_of_n))]
        m,i,p,result = find_best_model(results)
    else:
        result = fit(k, m, i, p, texts, wc)

    return result

