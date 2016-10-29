import doc_index.Document_Index as docIndex
import repository.Repository as repository
import requests
import struct

def getValidText(text):
    return text.encode('ascii', 'ignore')

def run(docID):
    url = getValidText(docIndex.getDocIDUrl(docID))
    status, pointer, checksum, docinfo, urllen, titlelen = docIndex.getDocIndex(docID)
    page = getValidText(requests.get(url).text)
    #print(url)
    #print(page)
    repoPosition = repository.addDocument(docID, url, page)
    status = 1
    pointer = repoPosition
    packed = struct.pack('BIIIHH', status, pointer, checksum, docinfo, urllen, titlelen)
    docIndex.setDocIndex(docID, packed)
    return repoPosition


