import os
from .IOUtil import result_dir, doc_dir

def load_stopwords():
    stopwords = set()
    for line in file(os.path.join(doc_dir, 'stopwords.txt')):
        word = line.strip().decode('utf-8')
        stopwords.add(word)
    return stopwords
