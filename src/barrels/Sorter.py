import lexicon.Lexicon as lexicon
import struct

def is_valid_wordID(wordIDBytes):
    for i in wordIDBytes:
        if i != 0:
            return True
    return False

def encode_forward_hits(docID, num_hits, hits):
    res_hits = None
    num_lists = num_hits/(2**5-1)
    for i in xrange(0, num_lists + 1):
        inverted_hit_data = docID << 5
        if i == num_lists:
            temp_num_hits = num_hits % (2**5-1)
        else:
            temp_num_hits = 2**5-1
        inverted_hit_data += temp_num_hits
        if res_hits == None:
            res_hits = struct.pack("I", inverted_hit_data)
        else:
            res_hits += struct.pack("I", inverted_hit_data)
        res_hits += hits[i * (2**5-1) * 2: i * (2**5-1) * 2 + temp_num_hits]
    return res_hits


def sort(forward = 'barrels/forward_index.bin', reverse = 'barrels/reverse_index.bin'):
    for wordID in xrange(0, lexicon.num_words()):
        hits = None
        with open(forward, 'r+b') as fp:
            fp.seek(0, 2)
            size = fp.tell()
            fp.seek(0, 0)
            while (fp.tell() < size):
                docID = struct.unpack("I", fp.read(4))[0]
                while is_valid_wordID(struct.unpack("BBB", fp.read(3))):
                    fp.seek(-3, 1)
                    hit_data = struct.unpack("I", fp.read(4))[0]
                    num_hits = hit_data & 0xFF
                    hit_wordID = hit_data >> 24 & 0xFFFFFF
                    if wordID == hit_wordID:
                        if hits == None:
                            hits = encode_forward_hits(docID, num_hits, fp.read(num_hits * 2))
                        else:
                            hits += encode_forward_hits(docID, num_hits, fp.read(num_hits * 2))
                    else:
                        fp.seek(num_hits*2, 1)
        #perhaps combine hits
        with open(reverse, 'a+b') as fp:
            # set word id pointer in lexicon
            if hits != None:
                fp.write(hits)