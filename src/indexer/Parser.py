import urllib2
import urlparse
import re
import sys
import time
import os
import lxml
from lxml import html
import anchors.Anchors as anchorHandler
import doc_index.Document_Index as docIndex
import repository.Repository as repository
import barrels.Forward_Index as forwardIndex
import URLResolver.URLResolver as urlresolver
import struct

def crawlWebpage(url):
    connection = urllib2.urlopen(url)
    page = connection.read()
    connection.close()
    return page

def clean_text(text):
    if text != None:
        newText = re.sub('[^A-Za-z0-9]+', ' ', text)
    else:
        return text
    return newText

def parse_page_for_title(page):
    tree = lxml.html.fromstring(page)
    return clean_text(tree.findtext('.//title'))

def parse_page_for_anchors(page):
    tree = lxml.html.fromstring(page)
    paths = tree.xpath('//a')
    anchors = []
    for i in paths:
        if i.text != None:
            text = clean_text(i.text)
            if len(text.replace(' ', '')) != 0:
                text = text.encode('ascii', 'ignore')
                anchors.append((text, i.get("href")))
    return anchors

def encode_title_hit(word, pos):
    cap = 1
    if word.islower():
        cap = 0
    imp = 7
    hit_type = 1
    value = (cap << 15)
    value += (imp << 12)
    value += (hit_type << 8)
    value += pos
    return struct.pack('H', value)
     

def encode_title_hits(cleaned_title):
    words = cleaned_title.split(" ")
    word_to_hits = {}
    for i in xrange(0, len(words)):
        encoded_title_hit = encode_title_hit(words[i], i)
        if encoded_title_hit != None:
            if words[i].lower() not in word_to_hits:
                word_to_hits[words[i].lower()] = encoded_title_hit[0] + encoded_title_hit[1]
            else:
                word_to_hits[words[i].lower()] += encoded_title_hit[0] + encoded_title_hit[1]
    #print word_to_hits
    return word_to_hits

# put it all together!
def parseFancyHits(docID, print_data=False):
    document_status, repository_pointer, checksum, docinfo_pointer, url_len, title_len = docIndex.getDocIndex(docID)
    repo_docID, url, page = repository.getDocument(repository_pointer)
    if page == None:
        print "PAGE IS NONE"
        print "page type: ", type(page)
    if repo_docID != docID:
        print "Repo DocID does not match the given DocID. Something is wrong with repository_pointer."
        
    # This is an array of touple(text, xpath)
    title = parse_page_for_title(page)
    if title == None:
        print("Title is none?")
        print("Doc ID: ", docID)
        print("Page: ")
        print(page)
        return None

    # this is an array of touple(text, fontSize)
    anchors = parse_page_for_anchors(page)
    for i in anchors:
        text, link = i
        #print "(%s): %s"%(link, text)
        anchorHandler.addAnchor(docID, link, text)
    document_status = 1
    position, url_length, title_length = docIndex.setDocInfo(url, title)
    docinfo_pointer = position
    url_len = url_length
    title_len = title_length
    packet = struct.pack('BIIIHH', document_status, repository_pointer, checksum, docinfo_pointer, url_len, title_len)
    docIndex.setDocIndex(docID, packet)
    
    hits = encode_title_hits(title)
    forwardIndex.addHits(hits, docID)
    return hits

def run(docID):
    return parseFancyHits(docID)