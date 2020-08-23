#!/usr/local/bin/python3
# <bitbar.title> Show Wallstreetbets hot posts.</bitbar.title>
# <bitbar.author> https://www.reddit.com/user/thestoicinvestor </bitbar.author>
# <bitbar.version>v2.0</bitbar.version>
# <bitbar.dependencies>Python3</bitbar.dependencies>

import re
import sys
import urllib.request
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer, SnowballStemmer 


ENGLISH_STOPWORD_SET = set(stopwords.words('english'))
ENGLISH_STEMMER = SnowballStemmer('english')


def process_word_list_with_nltk(word_list):
    token_list = [t.lower() for t in word_tokenize(word_list)]
    token_list = [t for t in token_list if (t.isalpha() and (t not in ENGLISH_STOPWORD_SET))]
    return [ENGLISH_STEMMER.stem(WordNetLemmatizer().lemmatize(t, pos='v')) for t in token_list] 


def count_words(sentance_list, word_dict):
    for sentance in sentance_list:
        word_list = process_word_list_with_nltk(sentance)
        for word in word_list:
            if word not in word_dict: 
                word_dict[word] = 0
            word_dict[word] += 1


def get_webpage(url):
    try:
        webpage = urllib.request.urlopen(url)
        return webpage.read()
    except urllib.error.URLError:
        return None


if __name__=='__main__':

    HOT_STOCK_POSTS = 'https://old.reddit.com/r/wallstreetbets/hot/'
    data = get_webpage(HOT_STOCK_POSTS)
    soup = BeautifulSoup(data, 'html.parser')

    list_of_links_unfiltered = soup.find_all('a')
    tag_filter = lambda tag: tag.has_attr('href') and tag['href'].find(
            '.reddit.com/r/wallstreetbets/comments') >= 0
    list_of_links = [i['href'] for i in list_of_links_unfiltered if tag_filter(i)]
    list_of_titles = [i.split('/')[-2].replace('_', ' ') for i in list_of_links]
    
    posts = dict(zip(list_of_titles, list_of_links))

    # crawl the pages and count the worlds in their paragraphs.
    is_reddit_metadata = lambda txt: txt.find('[–]') >= 0 or txt.find('[+]') >= 0
    for title in posts:
        word_count = {}
        href = posts[title]
        data = get_webpage(href)
        if not data:
            continue 
        soup = BeautifulSoup(data, 'html.parser')
        paragraph_list = [p.text for p in soup.find_all('p')
                if len(p.text) and not is_reddit_metadata(p.text)]
        count_words(paragraph_list, word_count)

        top_words = 40
        column_num = 2
        popular_words = sorted(word_count.items(), key = lambda x:x[1], reverse=True)[:top_words]
        print (title, '\n')
        for c in range(0, len(popular_words), column_num):
            print('\t\t\t'.join(["%s: %d" % (k,v) for k,v in popular_words[c:c+column_num]]))
        print ('\n\n')        
