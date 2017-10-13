SUMMARY_LENGTH = 50
NUM_TOPICS = 15


# Load the dataset
import pickle
with open('amazon_search_results.pickle', 'rb') as f:
    amzn = pickle.load(f)


# Get the editorial review for each object
from bs4 import BeautifulSoup
def strip_html(html):
    text = BeautifulSoup(html).text
    text = text.replace('\\n', ' ')
    text = text.replace('Product Description', '')
    return text

def get_ed_review(xml):
    html = BeautifulSoup(xml, 'xml').find('EditorialReview').text
    return strip_html(html)#utils.process_html(html)

ed_revs = []
for k,v in amzn.items():
    try:
        ed_revs.insert(0, get_ed_review(v))
    except Exception as e:
        print('No editorial review')


# Summarize the texts
import re
import gensim

summaries = []
for t in ed_revs:
    try:
        summaries.insert(0, gensim.summarization.summarize(t, word_count=SUMMARY_LENGTH))
    except ValueError as e:
        print(e)


# Process and flatten the summaries to feed to LDA
p_s = [utils.process_html(s) for s in summaries]
flat_er_sums = []
for e in p_s:
    for r in e:
        flat_er_sums.insert(0, r)

import gensim

dictionary = gensim.corpora.Dictionary(flat_er_sums)
corpus = [dictionary.doc2bow(s) 
          for s in flat_er_sums]
lda = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS)


# Output the results
for i in range(NUM_TOPICS):
    print()
    print('Topic: {}'.format(i))
    print(', '.join([dictionary.get(term) for term,_ in lda.get_topic_terms(i)]))


# Save the summaries
with open('amzn_summaries_{}'.format(SUMMARY_LENGTH), 'w') as f:
    for summary in summaries:
        f.write('{}\n'.format(summary))
