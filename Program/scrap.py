#importing required packages
import requests
import urllib
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import csv
import pandas as pd
from pandas import DataFrame
import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter
from nltk.corpus import stopwords
import numpy as np
import extraction

#Link is stored in variable u
u = str(input("Enter URL: "))
print("Writing data to files...")

#File is created to store information
filee = open('/Users/pavitra/pyexe/exeter/output_context2.txt','a')

#To find Homepage from given link
count = 0
listt = []
for val in u:
    listt.append(val)
    if val == '/':
        count+=1
    if count == 3 :
        break
    link = "".join([str(item) for item in listt])   
filee.write(f'Home Page Link: {link}\n\n\n')
print("Hope Page Link extracted...")
ll = list(link)

#Initialize the set of links (unique links)
internal = set()
external = set()
visited = 0
inn = list(internal)
ex = list(external)

#To check if given URL is valid
def valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

#Returns URL's found in a given webpage
def website_links(url):
    urls = set() 
    domain_name = urlparse(url).netloc # domain name of the URL without the protocol
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None: 
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path # remove URL fragments
        if not valid_url(href): 
            continue
        if href in internal: 
            continue
        if domain_name not in href: 
            if href not in external:
                filee.write(f'External link: {href}\n')
                external.add(href)
            continue
        filee.write(f'Internal link: {href}\n')
        urls.add(href)
        internal.add(href)
    filee.write(f'\n\n\n')
    return urls
print("Internal,External Links extracted...")
urls = website_links(u)

#Extract all links using crawl
def crawl(url, max_u=50):
    global visited
    visited += 1
    links = website_links(url)
    for link in links:
        if visited > max_u:
            break
        crawl(link, max_u=max_u)
crawl(u)

#To find Page title
def title(urls):
    f_title = []
    for val in urls:
        try:
            resource = requests.get(val)
            soup = BeautifulSoup(resource.text,'lxml')
        except:
            filee.write(f'URL not found\n')
        try:
            titles_final = soup.find('title').get_text()
        except:
            continue
        f_title.append(titles_final)
        try:
            titlee = set(f_title)
        except:
            pass
        for info in titlee:
            filee.write(f'Title: {info}\n')
    filee.write(f'\n\n\n')
print("Titles from website extracted...")
title(urls)

#To get image URL:
html = requests.get(u).text
extracted = extraction.Extractor().extract(html, source_url=u)
x = extracted.images

#To find meta tags from from all top level pages
response = requests.get(u)
soup = BeautifulSoup(response.text,'lxml')
metas = soup.find_all('meta')
m_name = [meta.attrs['name'] for meta in metas if 'name' in meta.attrs]
m_content = [meta.attrs['content'] for meta in metas if 'content' in meta.attrs]

#Returns the count of the links present in a website
filee.write(f'Total External links: {len(external)}\n')
filee.write(f'Total Internal links: {len(internal)}\n')
filee.write(f'Total links: {len(external) + len(internal)}\n')
filee.write(f'\n\n\n')
print("Total amount of links extracted...")

#To find the size of a website
def websize(url):
    try:
        res = urllib.request.urlopen(u)
        try:
            size = res.read()
            size_kb = len(size)
            size_mb = size_kb / 1024
            filee.write(f'Website Size: {size_mb} mb')
            filee.write(f'\n\n\n')
        except:
            filee.write(f'Can''t access size,website secured!')
    except:
        filee.write(f'Can''t access size,website secured!')
    print("Website size extracted...")
websize(u)

#To get data from a page
soup = BeautifulSoup(response.text,'lxml')
data = soup.stripped_strings
data_text = list(data)

#Convert list to string
def ltos(data_text):
  str_filterr = " " 
  return (str_filterr.join(data_text))
str_filterr = ltos(data_text) 
filee.write(f'Data from website: \n{str_filterr}\n\n\n')
print("Data from website extracted...")

#Stop words are removed
sW = set(stopwords.words('english'))
words = word_tokenize(str_filterr)
word_filter = []
for w in words:
    if w not in sW:
        word_filter.append(w)

#List without stopwords converted to string
def listtostr(word_filter):
  str_filter = " " 
  return (str_filter.join(word_filter))
str_filter = listtostr(word_filter) 
filee.write(f'Parsed Text: \n{str_filter}\n\n\n')
filee.write(f'\n\n')
print("Parsed text extracted...")

#String passed to get uni/bi grams
uni = nltk.word_tokenize(str_filter)
bi = ngrams(uni,2)
bi_l = list(bi)

#Top 20 uni/bi grams
word_fd = nltk.FreqDist(uni)
bigram_fd = nltk.FreqDist(bi_l)

#Export values to CSV
df1 = DataFrame({"Meta_Name":m_name})
df2 = DataFrame({"Meta_Content":m_content})
df3 = DataFrame({"Unigram":uni})
df4 = DataFrame({"Frequency Unigram":word_fd.most_common(20)})
df5 = DataFrame({"Bigram":bi_l})
df6 = DataFrame({"Frequency Bigram":bigram_fd.most_common(20)})
df8 = DataFrame({"Image_url":x})
final = pd.concat([df1,df2,df3,df4,df5,df6,df8],ignore_index = "False",axis=1)
export_csv = final.to_csv(r'/Users/pavitra/pyexe/exeter/output_csv2.csv',header=[ "Meta_Name", "Meta_Content" , "Unigram" , "Top 20 Frequency Unigram" , "Bigram" ,"Top 20 Bigram" , "Image URL" ])
print("Writing CSV files successfull...")
print("Writing text files successfull...")
