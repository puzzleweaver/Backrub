import anchors.Anchors as anchors
import struct
from urlparse import urldefrag, urlsplit, urljoin, urlparse
import sys, os
import doc_index.Document_Index as docIndex
import barrels.Forward_Index as forwardIndex
import links.Links as links
import urllib
import hashlib

def is_valid(url, qualifying=None):
    min_attributes = ('scheme', 'netloc')
    qualifying = min_attributes if qualifying is None else qualifying
    token = urlparse(url)
    return all([getattr(token, qualifying_attr)
                for qualifying_attr in qualifying])

def makeDocIndex(docID, url):
    #print("Making docIndex: [%d] %s" %(docID, url))
    #print "URL: ", url
    docIDindex = docIndex.getDocIndex(docID)
    if docIDindex == None:
        #print("Making docIndex: [%d] %s" %(docID, url))
        urlPos, length = docIndex.setUrlInList(url)
        docIDindex = [0, 0, 0, urlPos, length, 0]
    packet = struct.pack('BIIIHH', docIDindex[0], docIDindex[1], docIDindex[2], docIDindex[3], docIDindex[4], docIDindex[5])
    docIndex.setDocIndex(docID, packet)

def hashDocID(docID):
    return int(hashlib.md5(str(docID)).hexdigest()[:8], 16) & 0xF

def encode_anchor_hit(word, pos, docID):
    cap = 1
    if word.islower():
        cap = 0
    imp = 7
    hit_type = 2
    hash = hashDocID(docID)
    value = (cap << 15)
    value += (imp << 12)
    value += (hit_type << 8)
    value += (hash << 4)
    value += (pos & 0xF)
    return struct.pack('H', value)

def encodeAnchorHits(text, docID):
    words = text.split(" ")
    word_to_hits = {}
    for i in xrange(0, len(words)):
        encoded_anchor_hit = encode_anchor_hit(words[i], i, docID)
        if encoded_anchor_hit != None:
            if words[i].lower() not in word_to_hits:
                word_to_hits[words[i].lower()] = encoded_anchor_hit[0] + encoded_anchor_hit[1]
            else:
                word_to_hits[words[i].lower()] += encoded_anchor_hit[0] + encoded_anchor_hit[1]
    return word_to_hits


def putTextInForwardIndex(docID, text):
    #print("putting %s for docID %d in forward index" %(text, docID))
    hits = encodeAnchorHits(text, docID)
    forwardIndex.addHits(hits, docID)
    return hits

def addLink(doc1ID, doc2ID):
    links.addLink(doc1ID, doc2ID)
    
def isURLValid(url):
    return url != '' and is_valid(url)

# The URLresolver reads the anchors file and converts relative URLs into absolute URLs and in turn into docIDs.
# It puts the anchor text into the forward index, associated with the docID that the anchor points to.
# It also generates a database of links which are pairs of docIDs.
# The links database is used to compute PageRanks for all the documents.
def run():
    size = 0
    with open('anchors/anchors.bin', 'r+b') as fp:
        fp.seek(0, 2)
        size = fp.tell()
        fp.seek(0, 0)
        while fp.tell() < size:
            info = fp.read(8)
            docID, len_link, len_text = struct.unpack('IHH', info)
            link = fp.read(len_link)
            text = fp.read(len_text)

            doc2Url = link
            if urlsplit(link)[1] == '':
                doc1Url = docIndex.getDocIDUrl(docID)
                doc2Url = urljoin(doc1Url, link)
            doc2Url = urldefrag(urlsplit(doc2Url).geturl())[0]
            print "url: ", doc2Url
            if isURLValid(doc2Url):
                doc2ID = docIndex.getID(doc2Url)
                makeDocIndex(doc2ID, doc2Url)
                print("LEN HITS: %d" %len(putTextInForwardIndex(doc2ID, text)))
                addLink(docID, doc2ID)