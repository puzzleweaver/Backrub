import doc_index.Document_Index as docIndex

def make_list():
    size = 0
    id_list = []
    with open('doc_index/Document_Index.bin', 'r+b') as fp:
        fp.seek(0, 2)
        total_size = fp.tell()
        size = total_size / 20
    for i in xrange(0, size):
        documentInfo = docIndex.getDocIndex(i)
        if documentInfo[0] == 0:
            if documentInfo[2] == 0:
                id_list.append(i)
    return id_list