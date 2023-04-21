from typing import Dict, Tuple
import numpy as np
import gensim


def getWord2Id() -> Dict:
    '''
    Return a dict mapping word to id.
    '''
    sentence_files = ['dataset/train.txt',
                      'dataset/test.txt', 'dataset/validation.txt']
    word2id = {}
    for file in sentence_files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                for word in line.strip().split()[1:]:
                    if word not in word2id:
                        word2id[word] = len(word2id)
    return word2id


def getWord2Vec(word2id: Dict) -> np.array:
    '''
    Return a np.array of shape [len(word2id), word2vec.vector_size],
    mapping word to word2vec pretrained.
    '''
    file = 'dataset/wiki_word2vec_50.bin'
    word2vecModel = gensim.models.KeyedVectors.load_word2vec_format(
        file, binary=True)
    word2vec = np.array(np.zeros([len(word2id), word2vecModel.vector_size]))
    for word in word2id:
        if word in word2vecModel:
            word2vec[word2id[word]] = word2vecModel[word]
    return word2vec


def getData(path: str, word2id: Dict) -> Tuple[np.array, np.array]:
    '''
    Return a tuple of np.array, (word_ids, labels)
    '''
    wordIds = np.array([])
    labels = np.array([])
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip().split()
            word_ids = np.append(
                word_ids, [word2id[word] for word in line[1:]])
            labels = np.append(labels, int(line[0]))
    return wordIds, labels
