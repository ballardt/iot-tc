# API for text stuff

import pickle
from spacy.en import English
from bs4 import BeautifulSoup
import re

# Spacy filtering
def tokenize(text):
    parser = English()
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

# we want to lemmatize so dogs goes to dog and ran goes to run
# Lemmatization means to get the "dictionary entry" for a word
# Some documentation here http://www.nltk.org/howto/wordnet.html
def get_lemma(word):
    from nltk.corpus import wordnet as wn
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    elif wn.synsets(lemma, pos=wn.NOUN): 
        return lemma
    else:
        return None

def prepare_text_for_lda(text):
    import nltk
    en_stop = set(nltk.corpus.stopwords.words('english'))
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens if get_lemma(token)]
    return tokens

def run_lda(texts_tokens, num_topics=30, dictionary_save_name='dictionary.gensim', 
            corpus_save_name='corpus.pkl', model_save_name='model.gensim', print_topics=True):
    import gensim
    from gensim import corpora
    dictionary = corpora.Dictionary(texts_tokens)
    corpus = [dictionary.doc2bow(text) for text in texts_tokens]
    import pickle
    pickle.dump(corpus, open(corpus_save_name, 'wb'))
    dictionary.save(dictionary_save_name)
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics,
                                            id2word=dictionary, passes=30)
    ldamodel.save(model_save_name)
    if print_topics:
        print("TOPICS:")
        topics = ldamodel.print_topics(num_words=10)
        for topic in topics:
            print(topic)

def run_tfidf(texts, rand_score=False, num_clusters=34, perplexity=30, max_df=0.8, min_df=0.0):
    # texts: [(name, content{, label}), ...]
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.manifold import TSNE
    import pandas as pd
    import seaborn as sb
    from matplotlib import pyplot as plt
    
    tfidf_vectorizer = TfidfVectorizer(max_df=max_df, max_features=200000, min_df=min_df,
                                       stop_words='english', use_idf=True, 
                                       tokenizer=prepare_text_for_lda, ngram_range=(1,2))
    tfidf_matrix = tfidf_vectorizer.fit_transform([t[0] for t in texts])
    feature_names = tfidf_vectorizer.get_feature_names()
    feature_indices = {doc: tfidf_matrix[doc,:].nonzero()[0] for doc in range(tfidf_matrix.shape[0])}
    tfidf_scores = {doc: zip(ft_ind, [tfidf_matrix[doc,x] for x in ft_ind])
                    for doc, ft_ind in feature_indices.items()}

    # Clustering
    km = KMeans(n_clusters=num_clusters)
    km.fit(tfidf_matrix)
    clusters = km.labels_.tolist()
    tsne = TSNE(n_components=2, perplexity=30, random_state=1)
    tsne_pos = tsne.fit_transform(tfidf_matrix.toarray())

    # Graphing
    xs, ys = tsne_pos[:, 0], tsne_pos[:, 1]
    pre_df = list(zip([t[0] for t in texts], xs, ys, clusters))
    df = pd.DataFrame(pre_df)
    df.columns = ['name', 'x', 'y', 'category']
    plt.figure(figsize=(15,15))
    sb.pairplot(data=df, hue='category')

    # Adjusted Rand score
    if rand_score:
        from sklearn import metrics

        label_truth = []
        label_cluster = []
        df['content'] = [t[1] for t in texts]
        df['ground_truth'] = [t[2] for t in texts]
        df['ground_truth_factor'] = pd.factorize(df['ground_truth'])[0]
        ars = metrics.adjusted_rand_score(df['ground_truth_factor'], df['category'])
        print('Adjusted Rand score:', ars)
