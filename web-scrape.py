
# coding: utf-8

# # Preliminary

# In[18]:

# Only run this the very first time you use this journal to download
# sentence rules for nltk.
# Go to "Models" tab and double click "punkt". Close the window once
# it's downloaded. The package is 13MB.
import nltk
# nltk.download()


# In[150]:

from gensim.parsing.preprocessing import preprocess_string
from gensim.models import Word2Vec
from wikiapi import WikiApi
from nltk import tokenize
from bs4 import BeautifulSoup
import pandas as pd
import warnings
import requests
import pprint
import re

TIMEOUT = 5


# In[151]:

general_terms = ['iot', 'product', 'device']

# TODO automate, probably with emailAddress and CN
device_terms = {
    'Smart_Things': 'smartthings.com',
    'Amazon_Echo': 'amazon.com',
    'Netatmo_Welcome': 'netatmo.net',
    'Samsung_SmartCam': 'samsungsmartcam.com',
    'Dropcam': 'dropcam.com',
    'Belkin_Wemo_switch': 'xbcs.net',
    'TP-Link_Smart_Plug': 'tplinkcloud.com',
    'iHome': 'evrythng.com',
    'Belkin_Wemo_motion_sensor': 'xbcs.net',
    'LiFX_Smart_bulb': 'lifx.co',
    'Triby_speaker': 'invoxia.com',
    'PIX-STAR_Photo_frame': 'pix-star.com',
    'HP_printer': 'hpeprint.com'
}


# In[152]:

# Use this to avoid all of the InsecureErrorWarnings
warnings.filterwarnings('ignore')


# In[145]:

# Turn warnings back on
warnings.filterwarnings('default')


# # Components
# 
# ### General

# In[153]:

def get_sentences(text):
    return [preprocess_string(s) for s in tokenize.sent_tokenize(text)]

    
def get_most_similar(word, sentences):
    NO_SIMILAR_WORDS = []
    
    # Preprocess the input word, or don't if it doesn't result in
    # anything
    p_word = preprocess_string(word)
    if len(p_word) == 0:
        word = [word]
    else:
        word = p_word
    sentences = [s for s in sentences if len(s) > 0]
    
    # Get the most similar words to the input word if possible
    if len(sentences) > 0:
        model = Word2Vec(sentences, min_count=1)
        if any(w in model.wv.vocab for w in word):
            similar = model.wv.most_similar([w for w in word if w in model.wv.vocab])
        else:
            similar = NO_SIMILAR_WORDS
        del model
    else:
        similar = NO_SIMILAR_WORDS
        
    return similar


def get_url_plaintext(url):
    try:
        html = requests.get(url, verify=False, timeout=TIMEOUT).content
        soup = BeautifulSoup(html)

        # Ignore script and style tags so our corpus is only plaintext
        for script in soup(['script', 'style']):
            script.decompose()

        # Remove extra spaces or newlines
        text = re.sub(' +', ' ', soup.get_text().strip())
        text = re.sub('\n+', '\n', text)
    except requests.exceptions.RequestException: 
        print('Could not connect to {}'.format(url))
        text = ''
    
    return text


# ### Scrape a list of URLs

# In[154]:

def scrape_relevant_words(urls, terms):
    results = {}
    for url in urls:
        results[url] = {}
        text = get_url_plaintext(url)
        sentences = get_sentences(text)
        for term in terms:
            similar = get_most_similar(term, sentences)
            results[url][term] = similar
    return results 


# ### Scrape Google and Wikipedia

# In[155]:

def scrape_google(search_term, terms, num_sites=5):
    # Search Google for term and get the URLs of the top num_sites results
    html = requests.get('https://google.com/search?q={}'.format(search_term), timeout=TIMEOUT).content
    soup = BeautifulSoup(html)
    sites = soup.select('h3.r > a')[:num_sites]
    href_regex = '(/search|/url)?\?q=(.*?)&(.*)'
    sites = [re.search(href_regex, s.attrs['href']).group(2) 
             for s in sites 
             if re.compile('(.*)q=http(.*)').match(s.attrs['href'])]
    
    # Extract the most_similar words from the text on each site
    results = scrape_relevant_words(sites, terms+[search_term])
    
    return results


def scrape_wikipedia(search_term, terms):
    similar = {}
    
    # Search Wikipedia
    wiki = WikiApi()
    wiki_results = wiki.find(search_term)

    if len(wiki_results) > 0:
    # Get the most_similar words from the first search result
    # based on the term
        text = wiki.get_article(wiki_results[0]).content
        sentences = get_sentences(text)
        for term in [search_term]+terms:
            similar[term] = get_most_similar(term, sentences)
        
    return similar
    

def fetch_relevant_words(hostname, terms, num_sites=5):
    print(hostname)
    #all_similar = []
    all_results = {}
    if not hostname.startswith('http://'):
        hostname = 'http://'+hostname
    hostname_term = re.search('(http://)(.*)(\.)(.*)', hostname).group(2)
    
    # Homepage
    home_results = scrape_relevant_words([hostname], general_terms + [hostname_term])
    all_results['homepage'] = home_results
    
    # Google
    all_results['google'] = {}
    google_results = scrape_google(hostname_term, terms, num_sites)
    for k, v in google_results.items():
        all_results['google'][k] = v
    
    # Wikipedia
    wiki_results = scrape_wikipedia(hostname_term, terms)
    all_results['wiki'] = wiki_results
    
    return all_results


# # Implementation/scratch

# In[157]:

# Example of how to do it all: Google, Wiki, and the homepage
#results = {k: fetch_relevant_words(v, general_terms) for k, v in device_terms.items()}
#pprint.pprint(results)


# In[158]:

# Example of how to use scrape_relevant_words by itself
urls = [
    'https://en.wikipedia.org/wiki/Technology',
    'https://en.wikipedia.org/wiki/Science',
    'https://en.wikipedia.org/wiki/Outer_space'
]
terms = [
    'science',
    'nature',
    'math',
    'life'
]
pprint.pprint(scrape_relevant_words(urls, terms))

