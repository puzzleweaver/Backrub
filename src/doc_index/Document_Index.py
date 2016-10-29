import hashlib
import os
import struct

def hashUrl(url):
    return int(hashlib.md5(url).hexdigest()[:8], 16)& 0xFFFFFFFF

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def binarySearch(key):
    ensure_dir('doc_index/checksums.bin')
    fp = open('doc_index/checksums.bin', 'rb')
    fp.seek(0, 2)
    begin = 0
    end = fp.tell()

    while (begin < end):
        fp.seek((end - begin) / 8, 0)#8 is the size of each chunk of data(hash, id)
        line_key = struct.unpack('I', fp.read(4))
        if (key == line_key):
            id = struct.unpack('I', fp.read(4))
            fp.close()
            return id
        elif (key > line_key):
            begin = fp.tell()
        else:
            end = fp.tell()
    return None

def searchTempFile(key):
    ensure_dir('doc_index/temp-checksums.bin')
    fp = open('doc_index/temp-checksums.bin', 'rb')
    fp.seek(0, 2)
    begin = 0
    end = fp.tell()/8

    for i in xrange(0, end):
        fp.seek(i * 8, 0)
        temp = struct.unpack('I', fp.read(4))[0]
        if temp == key:
            id = struct.unpack('I', fp.read(4))[0]
            fp.close()
            return id
    return None

def makeNewId(hash):
    fp = open('doc_index/checksums.bin', 'rb')
    fp.seek(0, 2)
    size = fp.tell() / 8
    fp.close()

    fp = open('doc_index/temp-checksums.bin', 'ab+')
    fp.seek(0, 2)
    size = size + fp.tell()/8
    fp.write(struct.pack('II', hash, size))
    fp.close()
    return size

def getID(url):
    hash = hashUrl(url)
    id = binarySearch(hash)
    if id != None:
        return id
    id = searchTempFile(hash)
    if id != None:
        return id
    id = makeNewId(hash)
    return id

# documentStatus(1 byte)(0 == not parsed, 1 == parsed)
# pointer into repository(4 byte)
# a document checksum(4 byte)
# pointer into either docinfo(url and title) or URLlist(just url)(4 byte)
# url_len(2 bytes)
# title_len(2 bytes)
# other??(0 byte)
# TOTAL: (20 bytes)
def setDocIndex(id, info):
    ensure_dir('doc_index/document_index.bin')
    chunkSize = 20
    with open('doc_index/document_index.bin', 'r+b') as fp:
        fp.seek(chunkSize * id)
        fp.write(info)

def getDocIndex(id):
    ensure_dir('doc_index/document_index.bin')
    chunkSize = 20
    with open('doc_index/document_index.bin', 'r+b') as fp:
        fp.seek(chunkSize * id)
        chunk = fp.read(chunkSize)
        if chunk == '':
            return None
        return struct.unpack('BIIIHH', chunk)
    return None

#returns touple of (url, title)
def getDocInfo(position, url_length, title_length):
    ensure_dir('doc_index/docinfo.bin')
    with open('doc_index/docinfo.bin', 'r+b') as fp:
        fp.seek(position)
        url = fp.read(url_length)
        title = fp.read(title_length)
        return url, title
    return None

#returns touple of (position, url_length, title_length)
def setDocInfo(url, title):
    ensure_dir('doc_index/docinfo.bin')
    with open('doc_index/docinfo.bin', 'r+b') as fp:
        fp.seek(0, 2)
        position = fp.tell()
        url_length = len(url)
        title_length = len(title)
        fp.write(url)
        fp.write(title)
        return position, url_length, title_length
    return None

#returns url
def getUrlFromList(position, url_length):
    ensure_dir('doc_index/URLlist.bin')
    with open('doc_index/URLlist.bin', 'r+b') as fp:
        fp.seek(position)
        url = fp.read(url_length)
        return url
    return None

#returns touple of (position, url_length)
def setUrlInList(url):
    ensure_dir('doc_index/URLlist.bin')
    with open('doc_index/URLlist.bin', 'r+b') as fp:
        fp.seek(0, 2)
        position = fp.tell()
        url_length = len(url)
        fp.write(url)
        return position, url_length
    return None

def getDocIDUrl(docID):
    docIndex = getDocIndex(docID)
    if docIndex == None:
        return None
    if docIndex[0] > 0:#DOCUMENT IS PARSED
        docInfo = getDocInfo(docIndex[3], docIndex[4], docIndex[5])
        return docInfo[0]
    else:
        return getUrlFromList(docIndex[3], docIndex[4])