import lexicon.Lexicon as lexicon
import struct
import doc_index.Document_Index as docIndex

def search(word):
    wordID = lexicon.getValidID(word)
    if wordID == None:
        print("WordID is none... Word not found....")
        return
    pos = lexicon.get_reverse_index_ptr(wordID)
    #print("Word Position: %d" %pos)
    print "Searching: %s" %word
    with open('barrels/reverse_index.bin', 'r+b') as fp:
        fp.seek(pos, 0)
        for i in xrange(0, lexicon.get_nhits(wordID)):
            hits_data = struct.unpack("I", fp.read(4))[0]
            nhits = hits_data & 0b11111
            docID = (hits_data >> 5) & 0b111111111111111111111111111
            print "NUM HITS: %d" %nhits
            print "DOC ID: %d" %docID
            print "URL: %s" %docIndex.getDocIDUrl(docID)
            fp.seek(nhits * 2, 1)
