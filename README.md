These are the notes for using `notebooks/HierarchicalMultiDocSummarization.ipynb`. If I refer to "the Jupyter notebook", this is the file I'm talking about.

# Installation

Install Anaconda, or Miniconda with dependencies. I use Python 3, which is required due to incompatible encodings of gensim pickle objects between Python 2 and 3.

Anaconda dependencies:

* pandas
* numpy
* scipy
* jupyter

PIP dependencies:

* gensim
* nltk
* stanfordcorenlp

Be sure to install the PIP ones after sourcings the anaconda python. There are some additional steps for the PIP dependencies:

### gensim

I encountered an encoding issue and had to tweak the install locally:

1. Uninstall gensim if previously installed
2. Clone `https://github.com/jhlau/gensim`
3. Modify `gensim/gensim/utils.py` line 912 to read

    return _pickle.loads(f.read()**, encoding='latin1')

4. Go to the topmost gensim folder, then do

    $ pip install -e .

### nltk 
The first time you run nltk, you'll get an error because you don't have the stopwords data. Run `nltk.download('stopwords')` once to download the data. You don't have to run this line again, so remove it or comment it out. If you don't want `nltk_data` cluttering your home folder, you can move it to `/usr/share/`.

### stanfordcorenlp

Stanford CoreNLP is commonly used in the literature for NLP preprocessing. It's a Java server you can control with Python via the PIP package. To use it, install Java 1.8+ (JRE is fine), then download the package from https://stanfordnlp.github.io/CoreNLP. Unzip, then modify `CORENLP_PATH` in the Jupyter notebook to point to the unzipped directory.

### Misc.

I have my directory set up as `~/Projects/iot-diff/iot-tc/`, where `iot-tc` is the GitHub repo and `iot-diff` also contains things like the stanfordcorenlp directory. In the Jupyter notebook, set `BASE_PATH` to be the directory outside of `iot-tc`. If you make it `iot-tc`, you will also have to update the other paths to reflect this.

# Data

The .gitignore file is set up to ignore large datasets at the moment since they would make it difficult for me to push and pull with my shoddy home internet. For now, install the data manually:

## Doc2Vec

### apnews_dbow

This is a pretrained Doc2Vec model using 0.6G of AP News articles. Download from https://github.com/jhlau/doc2vec, then update `D2V_APNEWS_PATH` in the Jupyter notebook to point to doc2vec.bin.

## Train/test data

### DUC

The instructions are largely the same for the 2006 and 2007 datasets. I will use 200X to refer to either one. First, inflate the archive:

    $ gunzip DUC200X_Summarization_Documents.tgz
	$ tar -zxvf DUC200X_Summarization_Documents.tar
	$ cd DUC200X_Summarization_Documents

#### For 2006

    $ tar -zxvf duc2006_docs.tar.gz

Now update `DATA_DUC2006_RAW_PATH` to point to the `duc2006_docs` folder.

#### For 2007

    $ tar -zxvf duc2007_testdocs.tar.gz

Now update `DATA_DUC2007_RAW_PATH` to point to the `duc2006_testdocs/main` folder. Ignore the `update` folder.