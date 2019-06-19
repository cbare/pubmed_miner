"""
Tests for the lda module
"""
import numpy as np

import lda



def test_remove_stopwords():
    assert lda.remove_stopwords('the patients patient clinical treatment and with you at foobar') == 'foobar'


def test_bows_to_matrix():
    bows = [
        [(0, 1), (1, 3)],
        [(0, 2)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 3), (2, 2)]
    ]

    dictionary = {0:'a', 1:'b', 2:'c'}

    assert np.array_equal(lda.bows_to_matrix(bows, dictionary),
                          np.array([
                              [1,3,0],
                              [2,0,0],
                              [1,1,1],
                              [3,0,2],
                          ]))


def test_max_i():
    a = [(101, 0.123), (102, 0.456), (103,0.789), (105,0.765), (106,0.543)]
    assert lda.max_i(a) == 103
