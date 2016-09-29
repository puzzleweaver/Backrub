# temporarily
numBarrels = 64

# helper for saveToForwardBarrels
def seekNextDocIdFor(fileText, csid):  # helper method for saveToForwardBarrels
    if (csid == len(fileText)):
        return -1
    csid += 4  # seek past current docId
    numHits = 1
    while (numHits != 0):
        numHits = struct.unpack("L", fileText[csid:csid + 4])[0] & 0b11111111
        csid += 4 + numHits * 2  # fix this
    return csid


def saveToForwardBarrels(docId, hits):
    tempLex = {}
    for hit in hits:
        if (hit[0] in tempLex):
            tempLex[hit[0]] += hit[1]
        else:
            tempLex[hit[0]] = hit[1]

    barrels = []
    for i in xrange(numBarrels):
        barrels.append("")
    for key in tempLex.keys():
        if len(barrels[key >> 24]) == 0:
            barrels[key >> 24] = struct.pack("L", docId)
        barrels[key >> 24] += struct.pack("L", ((key & 0b111111111111111111111111) << 8) + (
            len(tempLex[key]) / 2 & 0b11111111)) + tempLex[key]

    for i in xrange(len(barrels)):
        if (len(barrels[i])):
            entry = barrels[i] + struct.pack("L", 0)  # null wordId with 0 hits
            try:  # read the file
                readFile = open('poople\\for\\b%i' % i, 'r')
                fileText = readFile.read()
                printBytes(fileText)
                readFile.close()
            except IOError:  # create the file if it's not there
                print("BARREL CREATED")
                fileText = entry
            else:
                sid = 0
                while True:
                    nsid = seekNextDocIdFor(fileText, sid)
                    if (nsid == -1):
                        print("ENTRY APPENDED")
                        fileText += entry
                        break
                    currentDocId = struct.unpack('L', fileText[sid:sid + 4])[0]
                    if (currentDocId == docId):
                        print("ENTRY REPLACED")
                        fileText = fileText[0:sid] + entry + fileText[nsid:]
                        break
                    elif (currentDocId > docId):
                        print("ENTRY INSERTED")
                        fileText = fileText[0:sid] + entry + fileText[sid:]
                        break
                    sid = nsid

            # write altered fileText back to file
            writeFile = open('poople\\for\\b%i' % i, 'w')
            writeFile.write(fileText)
            writeFile.close()

# helper for saveInvertedIndex
def seekNextDocIdInv(fileText, sid):
    if (sid == len(fileText)):
        return -1
    numHits = struct.unpack("L", fileText[sid:sid + 4])[0] & 0b11111
    return sid + 4 + numHits * 2

def saveInvertedIndex(barrelNum):
    try:
        readFile = open('poople\\for\\b%i' % barrelNum, 'r')
        fileText = readFile.read()
        readFile.close()
    except IOError:
        return

    # convert fileText to wordHits
    sid = 0
    wordHits = {}
    while True:
        nsid = seekNextDocIdFor(fileText, sid)
        if (nsid == -1):
            break
        entry = fileText[sid:nsid]
        docId = struct.unpack("L", entry[0:4])[0]
        masked = struct.unpack("L", entry[4:8])[0]
        wordId = masked >> 8
        numHits = masked & 0b11111111
        hits = entry[8:8 + numHits * 2]
        if (not wordId in wordHits.keys()):
            wordHits[wordId] = {}
        if (not docId in wordHits[wordId]):
            wordHits[wordId][docId] = hits
        else:
            wordHits[wordId][docId] += hits
        sid = nsid

    print("IT GOT THIS FAR")
    print(wordHits)

    # save hit lists to their inv files
    for wordId in wordHits.keys():

        # load and alter fileText
        try:
            readFile = open('poople\\inv\\b%i' % wordId, 'r')
            fileText = readFile.read()
            readFile.close()
            print("FILE READ SUCCESSFULLY")
        except IOError:
            print("EMPTY FILE")
            fileText = struct.pack("L", 0)

        numDocs = struct.unpack("L", fileText[0:4])[0]

        for docId in wordHits[wordId].keys():
            printBytes(fileText)
            print(docId)
            sid = 4  # numDocs is the first 4 chars
            entry = struct.pack("L", (docId << 5) + (len(wordHits[wordId][docId]) / 2)) + wordHits[wordId][
                docId]
            while True:
                nsid = seekNextDocIdInv(fileText, sid)
                if (nsid == -1):
                    print("ENTRY APPENDED")
                    fileText = struct.pack("L", numDocs + 1) + fileText[4:] + entry
                    break
                currentDocId = struct.unpack("L", fileText[sid:sid + 4])[0] >> 5
                if (currentDocId == docId):
                    print("ENTRY REPLACED")
                    fileText = fileText[0:sid] + entry + fileText[nsid:]
                    break
                elif (currentDocId > docId):
                    print("ENTRY INSERTED")
                    fileText = struct.pack("L", numDocs + 1) + fileText[4:sid] + entry + fileText[sid:]
                    break
                sid = nsid

        # write altered fileText
        writeFile = open('poople\\inv\\b%i' % wordId, "w")
        writeFile.write(fileText)
        writeFile.close()


# read from invertedIndices
def loadInvertedIndex(wordId):
    # read file
    try:
        readFile = open("poople\\inv\\%i" % wordId, "r")
        content = readFile.read()
        readFile.close()
    except IOError:
        print("WORD NOT IN BACKWARDS INDEXES")
        return {}
    # load hit lists
    hits = {}
    numDocs = struct.unpack("L", content[0:4])[0]
    currentSeekIndex = 4
    for i in xrange(numDocs):
        temp = struct.unpack("L", content[currentSeekIndex:currentSeekIndex + 4])[0]
        docId = temp >> 5
        numHits = temp & 0b11111
        hits[docId] = content[currentSeekIndex + 4:currentSeekIndex + 4 + 2 * numHits]
        currentSeekIndex += 4 + numHits * 2
    return hits
