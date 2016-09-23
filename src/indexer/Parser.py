import urllib2
import urlparse
import re
import sys
import time
import os
sys.path.append(os.path.abspath('lexicon/'))
import Lexicon as lex
import struct

def crawlWebpage(url):
    connection = urllib2.urlopen(url)
    page = connection.read()
    connection.close()
    return page

def formatText(text):
    trimmed = text.replace('\n', ' ')
    trimmed = trimmed.replace('\t', ' ')
    trimmed = trimmed.replace('_', ' ')
    trimmed = re.sub(r'[^\w]', ' ', trimmed)
    trimmed = " ".join(trimmed.split())
    return trimmed


def isValidText(text):
    trimmed = text.replace('\n', ' ')
    trimmed.replace('\t', ' ')
    trimmed = " ".join(trimmed.split())
    if len(text) > 1:
        return True
    for i in '. /!@#$%^&*()<>,.`~':
        if text == i:
            return False
    return text != ''

def getXPath(text, tree):
    real_text = tree.getpath(text.getparent())
    if 'div' not in real_text:
        return real_text
    tags = real_text.split('/')
    num_tags = len(tags)
    currentElement = text.getparent()
    ident = currentElement.get('id')
    count = 0
    while ident == None and count < num_tags:
        currentElement = currentElement.getparent()
        if currentElement == None:
            break
        ident = currentElement.get('id')
        count += 1
    if ident == None:
        return real_text
    else:
        real_text = '//*[@id="%s"]' %ident
        for i in xrange(num_tags-count, num_tags):
            tag = tags[i]
            if 'tr' in tag and tag != 'strong':
                if i > 0:
                    if 'tbody' not in tags[i-1]:
                        tag = 'tbody/' + tag
                else:
                    tag = 'tbody/' + tag
            real_text += '/' + tag
    return real_text


def parse_page_for_xpaths(page):
    from cStringIO import StringIO
    from lxml import etree

    #This is a touple array of (text, xpath)
    xpaths = []

    parser = etree.HTMLParser(remove_blank_text=True)
    tree   = etree.parse(StringIO(page), parser)
    find_text = etree.XPath("//text()")

    for text in find_text(tree):
        formatted_text = formatText(text)
        if isValidText(formatted_text):
            xpath = getXPath(text, tree)
            if 'script' not in xpath and 'body' in xpath:
                xpaths.append((formatted_text, xpath))
    return xpaths

def get_xpath_fontSize(xpath):
    if '/h6/' in xpath:
        return .83 * 16
    if '/h5/' in xpath:
        return .75 * 16
    if '/h3/' in xpath:
        return 1.17 * 16
    if '/h2/' in xpath:
        return 1.5 * 16
    if '/h1/' in xpath:
        return 2 * 16
    return 16

def get_xpath_data(xpaths):
    xpath_data = []
    for i in xpaths:
        text, xpath = i
        xpath_data.append((text, get_xpath_fontSize(xpath)))
    return xpath_data

def normalize_xpath_data(xpath_data, print_data = False):
    maxFontSize = 0
    minFontSize = 10000000#just a really high number...fix later
    for i in xpath_data:
        text, fontSize = i
        fontSize = float(fontSize)
        if maxFontSize < fontSize:
            maxFontSize = fontSize
        if minFontSize > fontSize:
            minFontSize = fontSize
    normalized_data = []
    for i in xpath_data:
        text, fontSize = i#fontSize is actually text. Convert it to a float
        trueFontSize = float(fontSize)
        div = float(maxFontSize - minFontSize)
        if div == 0:
            div = 1
        normalizedFontSize = int(round(float(trueFontSize - minFontSize)/div * 6))
        if print_data:
            print(fontSize, ' ~> %i'%normalizedFontSize)
        normalized_data.append((text, normalizedFontSize))
    return normalized_data

def isCapital(word):
    return not word.islower()

def breakTextIntoWordBundles(xpath_data, print_data = False):
    wordCount = 0
    words = []
    longestWordLen = 0
    longestWord = ''
    maxWordCount = 2**12-1
    for i in xpath_data:
        text, fontSize = i
        textWords = text.split(' ')
        for word in textWords:
            capital = isCapital(word)
            word = word.lower()
            words.append((word, capital, fontSize, min(wordCount, maxWordCount)))
            wordCount += 1
            if len(word) > longestWordLen:
                longestWordLen = len(word)
                longestWord = word
    if print_data:
        start = time.clock()
        print(start)
        print('Word Count:       %i' %wordCount)
        print('Longest Word: %s(%i)' %(longestWord, longestWordLen))
        print('=========================================')
        for wordBundle in words:
            word, capital, fSize, position = wordBundle
            tempWord = word
            spacesNeeded = longestWordLen - len(word)
            for i in xrange(0, spacesNeeded):
                tempWord += ' '
            print(tempWord + '\tcap: %r\tfSize: %i\tpos: %i'%(capital, fSize, position))
        stop = time.clock()
        print(stop)
        print(stop-start, "seconds")
    return words

def encodeHit(cap, fSize, pos):
    result = 0
    result += int(cap) << 15
    result += ((fSize << 12) & 0b0111000000000000)
    if pos > 0b111111111111:
        pos = 0b111111111111
    result += (pos & 0b0000111111111111)
    return struct.pack('H', result)

def encodePlainHits(parsedPlainHits, print_data = False):
    hitLists = []
    words = {}
    lex.load()
    for i in parsedPlainHits:
        word, cap, fSize, pos = i
        wordID = lex.getID(word)
        words[wordID] = word
        hitLists.append((wordID, encodeHit(cap, fSize, pos)))
    if print_data:
        for hitListKey in hitLists.keys():
            word = words[hitListKey]
            length = len(hitLists[hitListKey])
            print(word + '[%i]\t[%i hits]\t[%i bytes]:' %(hitListKey,  length/2, length))
            print(hitLists[hitListKey] + "\n")
    return hitLists

#put it all together!
def parsePlainHits(url, print_data = False):
    page = crawlWebpage(url)

    #This is an array of touple(text, xpath)
    xpaths = parse_page_for_xpaths(page)

    #this is an array of touple(text, fontSize)
    xpath_data = get_xpath_data(xpaths)

    #Font sizes are now normalized with the rest of the document
    normalized_fSize = normalize_xpath_data(xpath_data)

    #Array of touple(lowercase word, capital, normalizedFontSize, position)
    wordBundles = breakTextIntoWordBundles(normalized_fSize, print_data)

    return encodePlainHits(wordBundles, print_data)