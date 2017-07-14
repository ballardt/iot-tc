###############
# Preliminary #
###############
# Imports
from gensim.parsing.preprocessing import preprocess_string
from gensim.models import Word2Vec
from collections import defaultdict
from collections import Counter
from wikiapi import WikiApi
from nltk import tokenize
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import warnings
import requests
import pprint
import math
import sys
import re

# Globals
TIMEOUT = 5
GENERAL_TERMS = [
    'iot', 
    'product', 
    'device',
    'camera',
    'smarthub',
    'light',
    'home',
    'sensor',
    'platform',
    'printer',
    'speaker',
]
DEVICE_TERMS = {
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

# Use this to avoid all of the InsecureErrorWarnings
warnings.filterwarnings('ignore')
# Uncomment the below line and comment the above one to turn warnings back on
# warnings.filterwarnings('default')

##############
# Components #
##############
#
# General components
#
def get_sentences(text):
    """Process a document into a list of sentences"""
    return [preprocess_string(s) for s in tokenize.sent_tokenize(text)]
    
def get_most_similar(word, sentences):
    """Find the most similar words in the provided sentences to the given word"""
    NO_SIMILAR_WORDS = []
    
    # Preprocess the input word, or don't if it doesn't result in
    # anything.
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
    """Scrape the text from a webpage"""
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


def scrape_relevant_words(urls, terms, device_term=None):
    """Get most_similar words for a list of URLs and a list of terms"""
    results = {}

    for url in urls:
        results[url] = {}
        text = get_url_plaintext(url)
        sentences = get_sentences(text)

        for term in terms:
            similar = get_most_similar(term, sentences)
            results[url][term] = similar

        if device_term is not None:
            similar = get_most_similar(device_term, sentences)
            results[url]['device_term'] = similar

    return results 


#
# For Scraping Google and Wikipedia specifically
#
def scrape_google(search_term, terms, num_sites=5, return_sentences=False):
    """Get the most_similar words for the terms on the top n Google 
    search results"""
    # Search Google for term and get the URLs of the top num_sites results"""
    html = requests.get('https://google.com/search?q={}'.format(search_term), timeout=TIMEOUT).content
    soup = BeautifulSoup(html)
    sites = soup.select('h3.r > a')[:num_sites]
    href_regex = '(/search|/url)?\?q=(.*?)&(.*)'
    sites = [re.search(href_regex, s.attrs['href']).group(2) 
             for s in sites 
             if re.compile('(.*)q=http(.*)').match(s.attrs['href'])]
    
    # Extract the most_similar words from the text on each site
    if return_sentences:
        results = []
        for site in sites:
            text = get_url_plaintext(site)
            results = results + get_sentences(text)
    else:
        results = scrape_relevant_words(sites, terms+[search_term])
    
    return results


def scrape_wikipedia(search_term, terms, return_sentences=False):
    """Get the most_similar words to the terms provided on the first article
    found on Wikipedia"""
    similar = {}
    sentences = []
    
    # Search Wikipedia
    wiki = WikiApi()
    wiki_results = wiki.find(search_term)

    if len(wiki_results) > 0:
    # Get the most_similar words from the first search result
    # based on the term
        text = wiki.get_article(wiki_results[0]).content
        sentences = get_sentences(text)
        if not return_sentences:
            for term in [search_term]+terms:
                similar[term] = get_most_similar(term, sentences)
        
    if return_sentences:
        return sentences
    else:
        return similar
    

#
# Main algorithms: results from Google, Wikipedia, and the home site
#
def fetch_relevant_words(hostname, terms=[], num_sites=5):
    """Get the most_similar words for the terms from Google, Wikipedia, and
    each device's homepage. Train a separate Word2Vec on each source.

    DEPRECATED: use `composite_most_similar`. This function will be removed
    soon, and the rest of the code will be refactored to reflect this.
    """
    print(hostname)
    #all_similar = []
    all_results = {}
    if not hostname.startswith('http://'):
        hostname = 'http://'+hostname
    hostname_term = re.search('(http://)(.*)(\.)(.*)', hostname).group(2)
    
    # Homepage
    home_results = scrape_relevant_words([hostname], GENERAL_TERMS + [hostname_term])
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


def composite_most_similar(hostname, terms=[], num_sites=5):
    """Scrape Google, Wikipedia, and the device homepage for most_similar words.
    Everything is scraped first, then Word2Vec is trained on all of them."""
    print('Getting composite most_similar for {}...'.format(hostname))
    sentences = []
    
    if not hostname.startswith('http://'):
        hostname = 'http://'+hostname
    hostname_term = re.search('(http://)(.*)(\.)(.*)', hostname).group(2)
    
    # Homepage
    home_text = get_url_plaintext(hostname)
    sentences = sentences + get_sentences(home_text)
    
    # Google
    google_results = scrape_google(hostname_term, terms, num_sites, True)
    sentences = sentences + google_results
    
    # Wikipedia
    wiki_results = scrape_wikipedia(hostname_term, terms, True)
    sentences = sentences + wiki_results
    
    results = {t: get_most_similar(t, sentences) for t in [hostname_term]+terms}
    results['device_term'] = results.pop(hostname_term)
    
    return results


########
# Main #
########
if __name__=='__main__':
    # Load the data if a path is supplied; otherwise, fetch it
    if len(sys.argv) == 1:
        # Each row is a device, each column is a general_term, and the values are the 
        # list of most_similar words.
        # Get the most_similar for the terms for each device
        results = {k: composite_most_similar(v, GENERAL_TERMS) for k, v in DEVICE_TERMS.items()}
        # Tweak the dataframe so it looks nice
        df = pd.DataFrame(results).transpose()
        df.to_pickle('composite_DataFrame.bz2')
    else:
        df = pd.read_pickle(sys.argv[1])
    # Order the rows the same way as the paper
    df = df.reindex(DEVICE_TERMS.keys())
    # Add the hostname for each device to the row label
    df.index = df.index.map(lambda x: x + ' ({})'.format(DEVICE_TERMS[x]))
    # Get rid of the extra dict layer in the cell values and sort the words alphabetically
    df = df.apply(lambda row: [sorted([e[0] for e in r]) if len(r)>0 else None for r in row])
    # Only keep columns for each term
    df = df[['device_term']+GENERAL_TERMS]
    # Display it
    print('most_similar words for all devices across Google, Wiki, and their homepages:')
    print(df)
    print('----------------------------------')

    # Each row is one of the 30 most common most_similar words, one column is the
    # number of times that word appeared, and the other column is all of the devices
    # that had the word somewhere for some term.
    # I had trouble doing this all in pandas, so the solution below is ugly, but it
    # works and it's fast.
    # Fist, count how many times each word appears in a dict.
    collect = defaultdict(int)
    for a in df.values.tolist():
        for b in a:
            if b is not None:
                for c in b:
                    collect[c] += 1
    # Get the devices that reference each of the 30 most common words
    ctr = Counter(collect)
    mc = ctr.most_common(30)
    mentions = {x[0]: set() for x in mc}
    for idx, row in df.iterrows():
        row = row.dropna()
        for l in row:
            for w in l:
                if w in mentions:
                    mentions[w].add(idx)
    # Tweak the results so they look nice
    # Build a dict where the key is a word and the value is the list of all devices
    # containing that word in their scrape results
    m = {k: [', '.join(sorted(v))] for k, v in mentions.items()}
    # Create a dataframe
    m_df = pd.DataFrame(m).transpose()
    # Make the column name meaningful
    m_df.columns = ['devices']
    # Add a new column for the counts
    mc_dict = {x[0]:x[1] for x in mc}
    m_df['count'] = m_df.index.map(lambda i: mc_dict[i])
    # Print out the count and devices for each word sorted by highest count first
    print('30 most common words and the devices that mention them:')
    print(m_df[['count', 'devices']].sort_values(by='count', ascending=False))
    print('----------------------------------')

    # Create a heatmap where the rows and columns are devices, and the values are how
    # many words each of the devices have in common.
    # Get the number of words shared between each device
    collect = {}
    for idx1, row1 in df.iterrows():
        collect[idx1] = {}
        for idx2, row2 in df.iterrows():
            num_shared = 0
            for col in df.columns:
                l1 = df.loc[idx1][col]
                l2 = df.loc[idx2][col]
                if l1 is None:
                    l1 = []
                if l2 is None:
                    l2 = []
                num_shared += len(set(l1) & set(l2))
            collect[idx1][idx2] = num_shared
    # Set the size of the image
    fig, ax = plt.subplots(figsize=(7,6))
    # Create the heatmap with some parameters to make it look nice
    heatmap = sb.heatmap(pd.DataFrame(collect).reindex(df.index)[df.index], 
                         annot=True, linewidths=.5, vmax=8, ax=ax)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=90)
    heatmap.set_yticklabels(heatmap.get_yticklabels(), rotation=0)
    # Show the heatmap
    sb.plt.show()

    # Let the user know we're done
    print('Program execution finished')


#################
# Scratch/Misc. #
#################
# Example of how to use scrape_relevant_words by itself:
#
# urls = [
#     'https://en.wikipedia.org/wiki/Technology',
#     'https://en.wikipedia.org/wiki/Science',
#     'https://en.wikipedia.org/wiki/Outer_space'
# ]
# terms = [
#     'science',
#     'nature',
#     'math',
#     'life'
# ]
# scrape_relevant_words(urls, terms)
