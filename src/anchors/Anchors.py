import hashlib
import os
import struct

#################################################################
# docID(4bytes), len_link(2bytes), len_text(2bytes), link, text #
#################################################################
def addAnchor(docID, link, text):
    with open('anchors/anchors.bin', 'r+b') as fp:
        packet = struct.pack('IHH', docID, len(link), len(text)) + link + text
        fp.seek(0, 2)
        position = fp.tell()
        fp.write(packet)
        return position

def getAnchor(position):
    with open('anchors/anchors.bin', 'r+b') as fp:
        fp.seek(position)
        info = fp.read(8)
        docID, len_link, len_text = struct.unpack('IHH', info)
        link = fp.read(len_link)
        text = fp.read(len_text)
        return docID, link, text
    return None