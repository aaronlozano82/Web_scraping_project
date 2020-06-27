# -*- coding: utf-8 -*-
"""Der_Speigel_Web_Scraper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1St2VpaFHYVKgbeukMiuhK4aTRx7QgsHw

# <font color='lightgreen'> Der Spiegel Web Scraper </font>

---

## Import Dependencies
"""

# Import libraries for processing web text
from bs4 import BeautifulSoup
import requests

from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from lxml import html

# Import these dependencies if using Google Colab 
import nltk
nltk.download('punkt')

"""## Define All Functions"""

#@title Functions Hidden
# Get content of the webpage in an html string format by passing a url 
def get_html(url):
    page = requests.get(url)
    html_out = html.fromstring(page.content)
    text = page.text
    return html_out, text

# Convert html into soup to enable soup menthods
def get_soup(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup

# Extract hyperlinks from soup
def get_soup_links(soup):
    links = []
    for link in soup.find_all('a'):
        out_link = link.get('href')
        links.append(out_link)
    return links

# This function is for use with only the Topic pages on reuters.com
# Search through ALL links and filter for only those that are for actual articles
# links are formatted differently 
def get_articles_reuters_topics(links, old_url_set):
    articles = []
    for link in links:
        try:
            split_link = link.split('/')
            #if 'www.reuters.com'in split_link:
            if 'www.spiegel.de'in split_link:
              for topic in spiegel_topics:
                if topic in split_link:
                  link = link
                  if url_check(old_url_set, link) == False:
                    articles.append(link)
        except:
            continue
    articles = list(set(articles))
    old_url_set = set(articles + list(old_url_set))       
    return articles, old_url_set

# Check if new urls exists in the old_url_set. if yes, return True; if no, return False
# This function is used in the get_articles_reuters_topics function
def url_check(old_url_set, url):
    url_set = set([url])
    test_set = old_url_set & url_set
    if len(test_set) == 0:
        check = False
    else:
        check = True
    return check

# Get html strings from list of article weblinks
def get_html_reuters(articles):
    soup_list = []
    for article in articles:
        _, text = get_html(article)
        soup = get_soup(text)
        soup_list.append(soup)
    return soup_list

# Break out article_body, article_headline, and article_date from each article in provided hyperlinks and put into a dictionary called: out_list
def get_reuters_elements(soup_list, articles):
    out_list = []
    i = 0
    for article in soup_list:
        link = articles[i] # I don't think this is used at all here, which means there is no reason to require the second argument: articles
        i += 1
        try:
            article_body = article.find_all(body_class, {'class': body_tag})
            article_p = []
            for item in article_body:
                p_list = item.find_all('p')
                for p in p_list:
                    article_p.append(p.text)
            out_text = ' '.join(article_p)
            if out_text == '':
              continue
            if out_text.startswith('Besondere Reportagen'):
              continue
            out_dict = dict([('Text',out_text),('url',link)])
            out_list.append(out_dict)
        except:
            print('Unable to decode...skipping article...')
            continue

    return out_list

"""## Define URL Variables and Run Functions

<font color='orange'>Step 1.</font> Instantiate `tags and values`. Then instntiate `old_url_set` to be used in the `get_articles_reuters_topics` function. This is a running log of article links that will be compiled by iterating from steps 2 - 3.
"""

# Der Spiegel classes and tags
body_class = 'div'
headline_class = 'h2'
date_class = 'div'

body_tag = 'clearfix lg:pt-32 md:pt-32 sm:pt-24 md:pb-48 lg:pb-48 sm:pb-32'
headline_tag = 'lg:mb-20 md:mb-20 sm:mb-24'
date_tag = 'font-sansUI lg:text-base md:text-base sm:text-s text-shade-dark'

# Instantiate empty set to use a running list of hyperlinks while 
# running the scrape iterations
old_url_set = set([])

"""## Scrape Reuters Topics pages for all the most recent news articles. <font color='orange'>*Run Steps 2 - 3 for each instance of `url` variable, before moving on to the next steps*</font>

<font color='orange'>Step 2.</font> Define variables for each of Reuters main topics pages. Run this cell for each iteration by uncommenting a different url each time.
"""

# Define url variables
# NOTE: You must run these individually through the end of this section
# I didn't have time to figure out how to loop through all of them properly
# There is a section at the very bottom where you can see that I attempted but ran
# into a problem on one of the last functions. 

# Der Speigel Links
url = r'https://www.spiegel.de/'
#url = r'https://www.spiegel.de/plus/'
#url = r'https://www.spiegel.de/schlagzeilen/'
#url = r'https://www.spiegel.de/politik/deutschland/'#zero
#url = r'https://www.spiegel.de/politik/ausland/' #zero
#url = r'https://www.spiegel.de/panorama/'#one
#url = r'https://www.spiegel.de/wirtschaft/'#one
#url = r'https://www.spiegel.de/netzwelt/' #one
#url = r'https://www.spiegel.de/wissenschaft/' #one
#url = r'https://www.spiegel.de/geschichte/'
#url = r'https://www.spiegel.de/thema/leben/' #zero

spiegel_topics = ['plus', 'schlagzeilen', 'politik/deutschland', 'politik/ausland', 'panorama', 'wirtschaft', 'netzwelt', 'wissenschaft', 'geschichte', 'thema/leben']

"""## Scraper

<font color='orange'>Step 3.</font> Get HTML srting from web `url`
"""

# Pass the each instance of `url` variable to return the web page in HTML format and convert it to a string
html_string = str(get_html(url))
# Pass the HTML string (of the web page) to get its soup
soup = get_soup(html_string)
# Find ALL links on within the soup
links = get_soup_links(soup)
# Use this for Topics Pages only
# Filter out only those links that are for actual articles. We only want the "good" links
# This filters out things like links to images and advertisements or non-news worthy pages
articles, old_url_set = get_articles_reuters_topics(links, old_url_set)
print(len(articles))
# Print out the running list of hyperlinks to see how many you have
print(len(old_url_set))


"""## <font color='skyblue'>Parse soup from entire list of hyperlinks that you just accumulated</font>

<font color='orange'>Step 4.</font> Get soup for every link

<font color='orange'>Step 5.</font> Parse the soup for each link into `article_body`, `article_title`, and `article_date`. Create list of dictionaries for each web page

<font color='orange'>Step 6.</font> Run `TextBlob` on list of dictionaries to separate all sentences in a single list
"""

# Get soup for each one of the "good" links
url_links = list(old_url_set) # Convert the running set of links to a list for use in the following functions

soup_list = get_html_reuters(url_links)
print(f'Length of Soup List: {len(soup_list)}')
#print(soup_list[0])

# Parse the soup for each "good" link to get article text, title, and date
out_list = get_reuters_elements(soup_list, url_links)
print(f'Length of out_list: {len(out_list)}')
#out_list[0:2]
blob_sentences =[]
# Translate all articles to English
blob_full=[]
for i in range(len(out_list)):
  try:
    blob = out_list[i]['Text']
    trans = TextBlob(blob) # Enter string object
    trans = trans.translate(to='en')
    blob_full.append(trans)
    #print('\n', i+1, '\n',trans)
  except:
    print('got an error ...., skipping article....')
print(f'\nYou have {len(blob_full)} total blobs from {i+1} different articles')

# Break articles into sentences to conduct keyword search
# in next step
blob_sentences = []

for i in range(len(blob_full)):
  for item in blob_full[i].sentences:
    blob_sentences.append(item)
print(f'\nYou have {len(blob_sentences)} sentences from {i} different articles')

"""This is just a troubleshooting section to ensure you're `TextBlob` came out right. You should see a list of stentences, each starting with the word `Sentence`. Check this before moving to the next step."""

#@title Hidden for Troubleshooting
# print the first 6 sentences so you see what it looks like
blob_sentences[0]
len(blob_sentences)

"""## <font color='skyblue'> Keyword Search </font>

<font color='orange'>Step 7.</font> Determine key words used to search for event of interest in all the articles
"""

# Allow user to type in key words to search the text for
# Note this is case sensitive... so you need to make sure you enter your search 
# Try the entering the following to see some results: corona,COVID,death
filter_list = input("Enter key words to search for separated by commas. don't use spaces.\nSearch is case sensitive.\nExample search: America,United States,USA,U.S.A.,US,U.S.\n\n") #.title() # This is still a string... not a list yet

# Split filter words and convert into a list for itterating in the next step 

f = []
for word in (filter_list.split(",")):  # Split string into separate words, separate by comma
  f.append(word)                       # Generate new list containing each key word
f # This is now a list of key words that the user typed in

"""<font color='orange'>Step 8.</font> <font color='skyblue'> Search </font>  All sentences for Key Words and return only those consisting of a key word"""

# Instantiate list for holding the sentences
sentences = []

# Generate empty list of lists to store the sentences with your key words in them
for i in range(len(f)):
  sentences.append([])
#print('Here is what you just made, and empty list of lists: ', sentences, '\n')

# Generate lists of sentences for each key word and plug them into the list of lists from above            
for i in range(len(f)):
  for sentence in blob_sentences:
    if f[i] in sentence:
        sentences[i].append(sentence)
        
# Print number of sentences containing each key word
# Print out all sentences containing each key word
for i in range(len(f)):
  print('='*200)   
  print('\nThere are {} sentences containing the word: {} '.format(len(sentences[i]), f[i])) 
  print('-'*200)   


file_Der_Speigel = open("MyFileDer_Speigel.txt", "w") 
file_Der_Speigel.write(str(sentences))
file_Der_Speigel.close()
  #for sentence in sentences[i]:
      #print(sentence)

"""# <font color='orange'> Step 9. </font> Print <font color='skyblue'> Statistics </font>"""

# Print out sentiment values for each key word
print('Sentence | Polarity | Subjectivity | Sentiment | Avg Sentiment')
for i in range(len(f)):
  print('\n----------------------', f[i], '--------------------------------')
  for j in range(len(sentences[i])):
    polarity = sentences[i][j].sentiment[0]
    subjectivity = sentences[i][j].sentiment[1]
    bailey_sentiment = polarity * subjectivity

    print(j, '       |', round(polarity, 2), '    |', round(subjectivity, 2), '        |', round(bailey_sentiment, 2), '     |', 'avg')
  print('=============================================================')

# Test Section - This is used to test and see individual values to see if everything makes sense
# Change the indicies in between the brackets to compare the different outputs
print(sentences[0][0].sentiment)
print(np.average(sentences[0][0].sentiment))
print(round(np.average(sentences[0][0].sentiment), 3))

"""## Calculate <font color='yellow'> Sentiment </font>  for Each Key Word"""

sentiment = []

# Generate empty list of lists 
for i in range(len(f)):
  sentiment.append([])

#sentiment = [None] * len(f)

print('---Average Sentiment---')
for i in range(len(f)):
  try:
    for j in range(len(sentences[i])):
      sentiment[i].append(sentences[i][j].sentiment[0] * sentences[i][j].sentiment[1])  
      np.average(sentiment[i]) 
  except:
    print('The List is Empty')
  print(f[i], np.average(sentiment[i]))

# Test Section - This is used to test and see individual values to see if everything makes sense
# Change the indicies in between the brackets to compare the different outputs
print('1', np.average(sentiment[0]))
print('2', np.average(sentiment[1]))
print('3', np.average(sentiment[2]))
print('4', np.average(sentiment[3]))

"""## <font color='orange'> Plot Resutls  </font> 

---
"""

xaxis = []
for i in range(len(sentiment[0])): # sentiment[0] is the list of sentiments for the first key word
  xaxis.append(i)
print("The xaxis is {}.".format(xaxis))

plt.scatter(xaxis, sentiment[0])
plt.grid()
plt.title(f[0] + ' Sentiment Per Sentence', color='w')
plt.xlabel('Sentence', color='w')
plt.ylabel('Sentiment', color='w')
plt.xticks(color='w')
plt.yticks(color='w')
plt.ylim(-1,1)

xaxis = []
for i in range(len(sentiment[2])): # sentiment[0] is the list of sentiments for the first key word
  xaxis.append(i)
print("The xaxis is {}.".format(xaxis))

plt.scatter(xaxis, sentiment[2])
plt.grid()
plt.title(f[2] + ' Sentiment Per Sentence', color='w')
plt.xlabel('Sentence', color='w')
plt.ylabel('Sentiment', color='w')
plt.xticks(color='w')
plt.yticks(color='w')
plt.ylim(-1,1)

"""## <font color='black'>Step 10. Store All article data in DataFrame </font>  
<font color='grey'>Note: This is not just the filtered data, this contains all information from each web page. While not used in this project, it represents all of the original data used in this run. It can be used for reference.</font>
"""

# Put parsed data into Pandas DataFrame
df = pd.DataFrame(out_list)
df

"""<font color='orange'>Step 8.</font> <font color='skyblue'> Search </font>  All sentences for Key Words and return only those consisting of a key word"""