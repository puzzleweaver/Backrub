import hashlib
import os

lexicon = {}
new_words = []

def hashWord(word):
    return int(hashlib.md5(word).hexdigest()[:8], 16)& 0xFFFFFFFF

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def load(path = 'lexicon/wordList.txt', print_data = False):
    ensure_dir(path)
    input = open(path, 'r')
    list = input.read().split(",")
    input.close()

    id = 0
    for word in list:
        hash = hashWord(word)
        lexicon[hash] = id
        id += 1
    if print_data:
        print lexicon


def save(path = 'lexicon/wordList.txt'):
    ensure_dir(path)
    lexString = ''
    for word in new_words:
        lexString +=  ',' + word
    lexString = lexString[:]

    output = open(path, 'a')
    output.write(lexString)
    output.close()
    del new_words[:]


def getID(word):
    word = word.lower()
    if len(lexicon) == 0:
        print "LEXICON HAS NOT BEEN LOADED YET..."
        return
    hash = hashWord(word)
    if hash in lexicon:
        return lexicon[hash]
    else:
        id = len(lexicon)
        lexicon[hash] = id
        new_words.append(word)
        return id