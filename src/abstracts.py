import io
import requests
from collections import namedtuple
from lxml import etree


PMID_XPATH = 'MedlineCitation/PMID/text()'
TITLE_XPATH = 'MedlineCitation/Article/ArticleTitle/text()'
ABSTRACT_XPATH = 'MedlineCitation/Article/Abstract/AbstractText/text()'

filename = 'data/pmids_gold_set_unlabeled.txt'
with open(filename) as f:
    pubmed_ids = f.read().strip().split()


filename = 'data/pmids_test_set_unlabeled.txt'
with open(filename) as f:
    test_set_pubmed_ids = f.read().strip().split()


## parse text return type?
import re

url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
      'efetch.fcgi'
      '?db=pubmed'
      '&retmode=text'
      '&rettype=abstract'
      '&id={ids}').format(ids=','.join(pubmed_ids))

response = requests.get(url)

docs = re.split(r'\s*\n{3}', response.text.strip())

for doc in docs:
    m = re.match(r'^(\d+). ', doc)
    if not m:
        print(doc)

# PMID: 8270381  [Indexed for MEDLINE]
# PMID: 8712208  [Indexed for MEDLINE]
# PMID: 22229570  [Indexed for MEDLINE]
# ...

# apparently records aren't well separated by triple new-lines!


Article = namedtuple('Article', 'pmid title abstract')


url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
      'efetch.fcgi'
      '?db=pubmed'
      '&retmode=xml'
      '&rettype=abstract'
      '&id={ids}').format(ids=','.join(pubmed_ids))

## stream XML into lxml parser
response = requests.get(url, stream=True)
root = etree.parse(io.BytesIO(response.content))

for article in root.xpath('PubmedArticle'):
    print('-'*90)
    text_nodes = article.xpath('MedlineCitation/Article/Abstract/AbstractText/text()')
    print(join_text(text_nodes))



def join_text(nodes, delim='\n'):
    return delim.join(nodes) if nodes else None


def fetch_abstracts(pubmed_ids):
    """
    Fetches abstracts from the Entrez API.

    Returns a dict mapping pubmed ids to abstracts.
    """
    url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
          'efetch.fcgi'
          '?db=pubmed'
          '&retmode=xml'
          '&rettype=abstract'
          '&id={ids}').format(ids=','.join(pubmed_ids))

    ## stream XML response into lxml parser
    response = requests.get(url, stream=True)
    root = etree.parse(io.BytesIO(response.content))

    ## extract abstracts for each article
    return [Article(
            pmid = join_text(article.xpath(PMID_XPATH)),
            title = join_text(article.xpath(TITLE_XPATH)),
            abstract = join_text(article.xpath(ABSTRACT_XPATH)),
        )
        for article in root.xpath('PubmedArticle')]



fetch_abstracts(['8270381','8712208','12606185'])






from Bio import Entrez
from Bio.Entrez.Parser import StringElement

PMID_XPATH = 'MedlineCitation/PMID'
TITLE_XPATH = 'MedlineCitation/Article/ArticleTitle'
ABSTRACT_XPATH = 'MedlineCitation/Article/Abstract/AbstractText'


Entrez.email = 'christopherbare@gmail.com'


x = Entrez.read(Entrez.efetch(db="pubmed",
                              id=','.join(pubmed_ids),
                              rettype="abstract",
                              retmode="xml"))

def get_xpath(xpath, element):
    keys = xpath.split('/')
    e = element
    for key in keys:
        if e is None: break
        e = e.get(key)
    return e

def join_text(nodes, delim='\n'):
    if nodes:
        if isinstance(nodes, StringElement):
            return str(nodes)
        elif isinstance(nodes, str):
            return nodes
        elif isinstance(nodes, Sequence):
            return delim.join(nodes)
    return nodes

articles = [
    Article(
        pmid = join_text(get_xpath(PMID_XPATH, article)),
        title = join_text(get_xpath(TITLE_XPATH, article)),
        abstract = join_text(get_xpath(ABSTRACT_XPATH, article)),
    )
    for article in x['PubmedArticle']]

