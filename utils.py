from nltk.stem.porter import PorterStemmer
from urllib.parse import urljoin, urlsplit
from nltk import tokenize
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re

TIMEOUT = 5

# Get a raw HTML webpage from a URL
def fetch_webpage(url):
    try:
        html = requests.get(url, verify=False, timeout=TIMEOUT).content
    except requests.exceptions.RequestException: 
        print('Could not connect to {}'.format(url))
        html = ''
    return html

# Get a webpage and the webpages it links to, etc.
def fetch_deep(url, depth=2):
    all_html = {}
    all_urls = set()
    urls = set([url])
    for _ in range(depth):
        pages = [(fetch_webpage(u), '://'.join(urlsplit(u)[:2]), u) for u in urls if u not in all_urls]
        all_urls = all_urls.union(urls)
        urls = set([y for x in pages for y in get_page_links(x[0], x[1])])
        for p in pages:
            all_html[urljoin(p[1], p[2])] = process_html(p[0])
    return all_html

# Get a webpage's links
def get_page_links(html, base=None):
    soup = BeautifulSoup(html, parseOnlyThese=SoupStrainer('a', href=True))
    return [urljoin(base, link['href']) for link in soup.find_all('a')]

# Get plaintext from raw HTML
def scrape_html_text(html):
    soup = BeautifulSoup(html)
    # Ignore script and style tags so our corpus is only plaintext
    for script in soup(['script', 'style']):
        script.decompose()
    # Remove extra spaces or newlines
    text = re.sub(' +', ' ', soup.get_text().strip())
    text = re.sub('\n+', '\n', text)
    return text

# Get sentences for a piece of text
def get_sentences(text):
    sentences = [preprocess_string(s) for s in tokenize.sent_tokenize(text)]
    return sentences

# Preprocess a word
def preprocess_word(word):
    preprocessed_word = preprocess_string(word)
    # If we don't get anything, just send back the original
    if len(preprocessed_word) == 0:
        preprocessed_word = [word]
    return preprocessed_word

def process_html(html, min_sent_len=4):
    stops = set(line.strip() for line in open('../stopwords.txt'))
    stemmer = PorterStemmer()
    page_sents = []
    html = scrape_html_text(html)
    # Replace newlines with periods so they're treated as new sentences
    html = re.sub(r'\.?\n', '. ', html)
    # Split sentences
    sents = tokenize.sent_tokenize(html)
    sents = [sent for sent in sents if len(sent) >= min_sent_len]
    for s in sents:
        # Split each sentence into words (or punctuation)
        tokens = tokenize.word_tokenize(s)
        # Lowercase each word and remove punctuation
        tokens = [t.lower() for t in tokens if t.isalnum()]
        # Remove short/empty sentences
        if len(tokens) >= min_sent_len:
            # Stem and remove stop words
            page_sents.insert(0, [stemmer.stem(t) for t in tokens if t not in stops])
    return page_sents
