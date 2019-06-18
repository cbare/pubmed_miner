"""
functions for retrieving pubmed abstracts from the Entrez API.


example usage:

# run from the project root directory

$ python src/abstracts.py fetch --pmids-file data/pmids_gold_set_labeled.txt --output-dir data
$ python src/abstracts.py fetch --pmids-file data/pmids_test_set_unlabeled.txt
"""
import click
import io
import os, os.path
import requests
import sys
from collections import namedtuple
from lxml import etree

import lda


PMID_XPATH = 'MedlineCitation/PMID/text()'
TITLE_XPATH = 'MedlineCitation/Article/ArticleTitle/text()'
ABSTRACT_XPATH = 'MedlineCitation/Article/Abstract/AbstractText/text()'


Article = namedtuple('Article', 'pmid title abstract')



def read_pubmed_ids_from_file(path):
    """
    Read a list of pubmed IDs from the first column of a tab-delimited file.
    """
    pubmed_ids = []
    with open(path) as f:
        for line in f:
            fields = line.strip().split()
            if len(fields) > 0:
                pubmed_ids.append(fields[0])
    return pubmed_ids


def join_text(nodes, delim='\n'):
    """
    join xml text nodes into a string
    """
    return delim.join(nodes) if nodes else ''


def fetch_abstracts_as_xml(pubmed_ids):
    """
    Fetches abstracts from the Entrez API and return an lxml ElementTree.
    """
    url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
          'efetch.fcgi'
          '?db=pubmed'
          '&retmode=xml'
          '&rettype=abstract'
          '&id={ids}').format(ids=','.join(str(pmid) for pmid in pubmed_ids))

    ## stream XML response into lxml parser
    response = requests.get(url, stream=True)
    return etree.parse(io.BytesIO(response.content))



def fetch_abstracts_to_files(pubmed_ids, output_dir):
    """
    Fetch abstracts from pubmed and write each abstract as an XML file in the
    specified output directory.

    Returns a list of output paths.
    """
    root = fetch_abstracts_as_xml(pubmed_ids)

    ## write each abstract to an xml file separately
    paths = []
    for article in root.xpath('PubmedArticle'):
        pmid = join_text(article.xpath(PMID_XPATH))
        path = os.path.join(output_dir, f'{pmid}.xml')
        etree.ElementTree(article).write(path,
                                         encoding='utf-8',
                                         xml_declaration=True,
                                         pretty_print=True)
        paths.append(path)

    return paths


def fetch_abstracts(pubmed_ids):
    """
    Fetches abstracts from the Entrez API.

    Returns a dict mapping pubmed ids to abstract objects
    """
    root = fetch_abstracts_as_xml(pubmed_ids)

    ## extract abstracts for each article
    return [Article(
            pmid = join_text(article.xpath(PMID_XPATH)),
            title = join_text(article.xpath(TITLE_XPATH)),
            abstract = join_text(article.xpath(ABSTRACT_XPATH)),
        )
        for article in root.xpath('PubmedArticle')]



## tell Click that we want a group of subcommands
@click.group()
def cli():
    pass


@cli.command()
@click.option('--output-dir', help='output directory.')
@click.option('--pmids-file', help='path to file containing pubmed ids')
@click.argument('pubmed-ids', nargs=-1)
def fetch(output_dir, pmids_file, pubmed_ids):
    """
    Command to fetch abstracts from pubmed given a list of pubmed IDs.

    Write output to stdout or, if output directory is given, to XML files in
    that directory.
    """
    if pmids_file:
        pubmed_ids = list(pubmed_ids) + read_pubmed_ids_from_file(pmids_file)

    if output_dir:
        paths = fetch_abstracts_to_files(pubmed_ids, output_dir)
        print(f'wrote {len(paths)} files.')
    else:
        articles = fetch_abstracts(pubmed_ids)
        for article in articles:
            print('\n\n')
            print(f'PMID: {article.pmid}')
            print(f'title: {article.title}')
            print(f'abstract: {article.abstract}')
        print(f'\n\nfetched {len(articles)} abstracts.\n')


@cli.command()
@click.option('--output-path', help='output path.')
@click.option('--pmids-file', help='path to file containing pubmed ids')
@click.option('--best-of-n', type=int, default=None)
@click.option('--discretize', is_flag=True)
def cluster(output_path, pmids_file, best_of_n, discretize):
    """
    """
    pubmed_ids = read_pubmed_ids_from_file(pmids_file)

    articles = fetch_abstracts(pubmed_ids)

    params = {
        'k': 5,
        'min_occur': 11,
        'iterations': 20,
        'passes': 300,
    }

    result = lda.cluster(articles, params, best_of_n=best_of_n)

    if output_path:
        with open(output_path, 'wt') as out:
            lda.print_result(pubmed_ids, result, discretize=discretize, out=out)
    else:
        lda.print_result(pubmed_ids, result, discretize=discretize)





if __name__ == '__main__':
    cli()
