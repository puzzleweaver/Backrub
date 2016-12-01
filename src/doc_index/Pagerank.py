import random
import math
import struct

d = 0.85
links = 0
pagerank = 0
N = 0

def calculatePagerank():
    initClass()
    # start at random docID
    currentDocID = math.floor(N*random.random())

    # calculate pageRank
    with open('links/links.bin') as fp:
        # randomly walk through pageranks
        
        # calculate new pagerank of currentDocID
        bytes = 0
        calcSum = 0.
        links.seek(0, 0)
        while True:
            bytes = links.read(8)
            if len(bytes) != 8:
                break
            a,b = struct.unpack("II", bytes)
            print("%i:%i\n" % (a, b))
            if(b == currentDocID):
                calcSum += getPagerank(a)/getLinksFrom(a);
        newPagerank = (1-d) + d*calcSum

# set all pageranks to be equal
def resetPagerank():
    initClass()
    datum = struct.pack("f", 1.0/N)
    pagerank.seek(0, 0)
    pagerank.truncate()
    for i in range(N):
        f.write(datum)

# extends pagerank.bin with entries for new docIDs
def extendPagerank():
    initClass()
    f.seek(0, 2)
    f.tell()
    # do stuff
    datum = struct.pack("f", 1.0/N)
    for i in range(N):
        pagerank.write(datum)

#--------------------
# helper methods:

def getPagerank(docID):
    pagerank.seek(docID*4, 0)
    return struct.unpack('f', pagerank.read(4))

def initClass():
    # set N to the highest docID
    global N
    with open('doc_index/Document_Index.bin') as fp:
        fp.seek(0, 2);
        N = fp.tell()/20;

    # open links/links.bin
    try:
        print("ran")
        global links
        links = open('links/links.bin', 'r+b')
    except Error as err:
        print(err)
        
        # open links/links.bin
    try:
        global pagerank
        pagerank = open('doc_index/pagerank.bin', 'r+b')
    except:
        print("could not open pagerank.bin")
