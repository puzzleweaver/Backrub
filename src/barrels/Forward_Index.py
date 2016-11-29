import lexicon.Lexicon as lexicon
import struct

#Hits being a dictionary of [word] ~> hits
def addHits(hits, docID):
    packet = struct.pack("I", docID)
    for key in hits.keys():
        wordId = lexicon.getID(key)
        length = len(hits[key])/2
        res = (wordId & 0xFFFFFF) << 8
        res += (length & 0xFF)
        if not(0 <= res <= 4294967295):
            print("Res: %d" %res)
            print("WordID: %d" %wordId)
            print("length: %d" %length)
        packet += struct.pack('I', res)
        packet += hits[key]
        #print("adding hit...")
        #print(hits[key])
    packet += struct.pack('BBB', 0, 0, 0)#NULL WORD ID
    with open('barrels/forward_index.bin', 'a+b') as fp:
        fp.write(packet)