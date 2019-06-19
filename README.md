# pubmed_miner
A demo on retrieving and clustering pubmed abstracts.


## Methods

I tried [k-means](notebooks/k-means.ipynb) and [latent dirichlet allocation](notebooks/experiments_with_lda.ipynb) (LDA).

The main advantage of LDA is it's ability to compute a discrete distribution over all topics for a given input document. Thus, if a document is pertains to more than one topic, it's topic relavance can be assigned proportionally. Since these abstracts are focused on specific topics, this ability is probably not especially well suited to the question here and LDA has costs in terms of model and computational complexity.

After some tuning and data preparation, I was able to get a decently performing lda model. The preprocessing steps were:
  - filtering punctuation
  - filtering numbers
  - removing stopwords
  - porter stemming
  - filtering out low-occurrence words
  - adding bigrams and trigrams

In contrast, k-means on tf-idf vectors performed well out of the box, having the addition advantage of training faster. I didn't explore preprocessing as much with k-means due to limits on time.

On the unlabeled test-set, the two models acheived very similar results. Kmeans agreed with the highest weighted LDA topic for 73 out of 77 abstracts. (See the notebook [lda-vs-kmeans.ipynb](notebooks/lda-vs-kmeans.ipynb))

Although both methods perform decently, kmeans might be a better choice. It's simpler, faster and could probably perform at least as well given a little more attention to feature engineering. If we're looking for an assignment to a single cluster, we're not playing to the strength of LDA.


## Notebooks

All of the prototyping was done in [jupyter](https://jupyter.org/) notebooks. There are three of them:

- [k-means](notebooks/k-means.ipynb)
- [latent dirichlet allocation](notebooks/experiments_with_lda.ipynb)
- [lda-vs-kmeans.ipynb](notebooks/lda-vs-kmeans.ipynb)


These look OK when viewed in github, but it's more fun to run them, which you can do with the command:

```
jupyter notebooks
```


## Running pubmed_miner

The tests and code can be run either on the local machine using a virtual environment (venv) or via a Docker container.

### Running in a virtual environment

Set up a virtual environment with the following commands:

```
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```


#### Running the pubmed clusterizer

The following will retrieve abstracts whose pubmed IDs are given in the file _pmids_gold_set_unlabeled.txt_ and cluster them by LDA.

The _--discretize_ parameter collapses the resulting probabilities to a single cluster assignment, thereby somewhat defeating the purpose of LDA.

```
PYTHONPATH=`pwd`/src python src/abstracts.py cluster --pmids-file data/pmids_gold_set_unlabeled.txt --discretize --best-of-n 5
```

#### Running tests

Testing is important. Analytics code is often difficult to test due to complex dependencies. The _tests_ folder holds a few token tests. To run them:

```
PYTHONPATH=`pwd`/src py.test -v -W ignore::DeprecationWarning
```


### Running in a Docker container

A docker image can be built with the command:

```
docker build -t christopherbare/pubmed_miner:latest .
```

Run tests in Docker:

```
./run-tests-in-docker.sh
```

Run clusterizer in Docker

```
./run-in-docker.sh --help
```

