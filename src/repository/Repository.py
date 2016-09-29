import hashlib
import os
import struct
import zlib

#######################################################################
# docID(4bytes), ecode(?), urllen(2bytes), pagelen(4bytes), url, page #
#######################################################################
def makePacket(docID, url, page):
    urllen = len(url)
    pagelen = len(page)
    packet = struct.pack('III', docID, urllen, pagelen) + url + page
    return packet

def unpackPacket(packet):
    docID, urllen, pagelen = struct.unpack('III', packet[0:12])
    url = packet[12:12+urllen]
    page = packet[12+urllen:12+urllen+pagelen]
    return docID, url, page

def compressPacket(packet):
    return zlib.compress(packet)

def decompressPacket(packet):
    return zlib.decompress(packet)

###########################
# sync(?), length(4bytes) #
###########################
def addDocument(docID, url, page):
    packet = makePacket(docID, url, page)
    compressedPacket = compressPacket(packet)
    fullpacket = struct.pack('I', len(compressedPacket)) + compressedPacket
    with open('repository/repository.bin', 'r+b') as fp:
        fp.seek(0, 2)
        position = fp.tell()
        fp.write(fullpacket)
        return position
    return None

def getDocument(position):
    with open('repository/repository.bin', 'r+b') as fp:
        fp.seek(position)
        length = struct.unpack('I', fp.read(4))[0]
        compressedPacket = fp.read(length)
        packet = decompressPacket(compressedPacket)
        docID, url, page = unpackPacket(packet)
        return docID, url, page
    return None


