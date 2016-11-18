import lexicon.Lexicon as lexicon
import struct
import doc_index.Document_Index as docIndex

def search(word):
    wordID = lexicon.getValidID(word)
    if wordID == None:
        print("WordID is none... Word not found....")
        return
    pos = lexicon.get_reverse_index_ptr(wordID)#  +1
    #print("Word Position: %d" %pos)
    print "Searching: %s" %word
    with open('barrels/reverse_index.bin', 'r+b') as fp:
        fp.seek(pos, 0)
        hits_data = struct.unpack("I", fp.read(4))[0]
        nhits = hits_data & 0b11111
        hits_data -= nhits
        hits_data = hits_data >> 5
        docID = hits_data
        #print "NUM HITS: %d" %nhits
        #print "DOC ID: %d" %docID
        print "URL: %s" %docIndex.getDocIDUrl(docID)
