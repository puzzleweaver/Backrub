import lexicon.Lexicon as lexicon
import struct

#Hits being a dictionary of [word] ~> hits
def addHits(hits, docID):
    packet = struct.pack("I", docID)
    for key in hits.keys():
        wordId = lexicon.getID(key)
        length = len(hits[key])
        res = wordId << 24
        res += (length & 0xFF)
        packet += struct.pack('I', res)
    packet += struct.pack('B', 0)
    with open('anchors/anchors.bin', 'a+b') as fp:
        fp.write(packet)