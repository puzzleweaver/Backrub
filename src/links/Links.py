import hashlib
import os
import struct

######################################
# docIDFrom(4bytes), docIDTo(4bytes) #
######################################
def addLink(docIDFrom, docIDTo):
    with open('links/links.bin', 'r+b') as fp:
        packet = struct.pack('II', docIDFrom, docIDTo)
        fp.seek(0, 2)
        position = fp.tell()
        fp.write(packet)
        return position

def getLinkPair(position):
    with open('links/links.bin', 'r+b') as fp:
        fp.seek(position)
        info = fp.read(8)
        docIDFrom, docIDTo = struct.unpack('II', info)
        return docIDFrom, docIDTo
    return None