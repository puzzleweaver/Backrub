import lexicon.Lexicon as lexicon
import struct

def is_valid_wordID(wordIDBytes):
    for i in wordIDBytes:
        if i != 0:
            return True
    return False

def encode_forward_hits(docID, num_hits, hits):
    res_hits = None
    if num_hits > (2**5-1):
        print("Num hits is too much...")
        return ''
    num_lists = num_hits/(2**5-1)
    inverted_hit_data = docID << 5
    inverted_hit_data += num_hits
    res_hits = struct.pack("I", inverted_hit_data)
    res_hits += hits
        #print "Doc ID [%d] Num Hits[%d]" %(docID, num_hits)
        #print "Inverted Hit Data: ", bin(struct.unpack("I", res_hits)[0])
    return res_hits


def sort(forward = 'barrels/forward_index.bin', reverse = 'barrels/reverse_index.bin'):
    for wordID in xrange(0, lexicon.num_words()):
        hits = None
        nhits = 0
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
                    hit_wordID = (hit_data >> 8) & 0xFFFFFF
                    if wordID == hit_wordID:
                        if hits == None:
                            hits = encode_forward_hits(docID, num_hits, fp.read(num_hits * 2))
                        else:
                            hits += encode_forward_hits(docID, num_hits, fp.read(num_hits * 2))
                        nhits += 1
                    else:
                        fp.seek(num_hits*2, 1)
        #perhaps combine hits
        with open(reverse, 'a+b') as fp:
            # set word id pointer in lexicon
            if hits != None:
                fp.seek(0, 2)
                pos = fp.tell()
                lexicon.set_reverse_index_ptr(wordID, pos)
                lexicon.set_nhits(wordID, nhits)
                fp.write(hits)