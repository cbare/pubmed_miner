"""
Tests for abstracts module
"""
from abstracts import *


def test_join_text():
    assert join_text(['a','b','c'], delim='') == 'abc'
    assert join_text([]) == ''
    assert join_text(None) == ''
