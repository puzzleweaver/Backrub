import hashlib
import os
import struct

def is_ascii(text):
    if isinstance(text, unicode):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    else:
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    return True

def is_ascii_str(s):
    return all(ord(c) < 128 for c in s)

#################################################################
# docID(4bytes), len_link(2bytes), len_text(2bytes), link, text #
#################################################################
def addAnchor(docID, link, text):
    if link == None:
        return
    if text == None:
        text = ""
    if is_ascii(link) and is_ascii(text):
        if isinstance(text, unicode):
            text.encode('ascii')
        if isinstance(link, unicode):
            link.encode('ascii')
        assert is_ascii_str(text)
        assert is_ascii_str(link)
        with open('anchors/anchors.bin', 'r+b') as fp:
            packet = struct.pack('IHH', docID, len(link), len(text)) + link + text
            fp.seek(0, 2)
            position = fp.tell()
            fp.write(packet)
            return position
    return None

def getAnchor(position):
    with open('anchors/anchors.bin', 'r+b') as fp:
        fp.seek(position)
        info = fp.read(8)
        docID, len_link, len_text = struct.unpack('IHH', info)
        link = fp.read(len_link)
        text = fp.read(len_text)
        return docID, link, text
    return None