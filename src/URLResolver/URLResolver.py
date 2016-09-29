from src.anchors import Anchors as anchors
import struct
from urlparse import urljoin, urlsplit
import sys, os
from src.anchors import Document_Index as docIndex
from src.links import Links as links

def makeDocIndex(docID, url):
    docIndex = docIndex.getDocIndex(docID)
    if docIndex == None:
        urlPos = docIndex.setUrlInList(url)
        docIndex = [0, 0, 0, urlPos, len(url), 0]
    packet = struct.pack('BIIIHH', docIndex[0], docIndex[1], docIndex[2], docIndex[3], docIndex[4])
    docIndex.setDocIndex(docID, packet)

def putTextInForwardIndex(docID, text):
    return

def addLink(doc1ID, doc2ID):
    links.addLink(doc1ID, doc2ID)

# The URLresolver reads the anchors file and converts relative URLs into absolute URLs and in turn into docIDs.
# It puts the anchor text into the forward index, associated with the docID that the anchor points to.
# It also generates a database of links which are pairs of docIDs.
# The links database is used to compute PageRanks for all the documents.
def run():
    size = 0
    with open('anchors/anchors.bin', 'r+b') as fp:
        fp.seek(0, 2)
        total_size = fp.tell()
        size = total_size/8
    for i in xrange(0, size):
        position = i*8
        docID, link, text = anchors.getAnchor(position)
        doc2Url = link
        if urlsplit(link)[1] == '':
            doc1Url = docIndex.getDocIDUrl(docID)
            doc2Url = urljoin(doc1Url, link)
        doc2Url = urlsplit(doc2Url).geturl()
        doc2ID = docIndex.getID(doc2Url)
        makeDocIndex(doc2ID, doc2Url)
        putTextInForwardIndex(doc2ID, text)
        addLink(docID, doc2ID)




