from data_reader import getWord2Id, getData
from tqdm import tqdm
from transformers import pipeline

if __name__ == '__main__':
    word2id = getWord2Id()
    test_contents, test_labels = getData('dataset/test.txt', word2id)
    classifier = pipeline('sentiment-analysis', 'bert-base-chinese')
    TP, FP, FN, TN = 0, 0, 0, 0
    id2word = {v: k for k, v in word2id.items()}
    for i in tqdm(range(len(test_contents))):
        content = ''.join([id2word[j] for j in test_contents[i] if j != 0])
        output = classifier(content)
        if output[0]['label'] == 'LABEL_0':
            output = 0
        else:
            output = 1
        if output == 1 and test_labels[i] == 1:
            TP += 1
        elif output == 1 and test_labels[i] == 0:
            FP += 1
        elif output == 0 and test_labels[i] == 1:
            FN += 1
        elif output == 0 and test_labels[i] == 0:
            TN += 1
    print('TP: %d, FP: %d, FN: %d, TN: %d' % (TP, FP, FN, TN))
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2 * precision * recall / (precision + recall)
    accuracy = (TP + TN) / (TP + FP + FN + TN)
    print('precision: %.4f, recall: %.4f, f1: %.4f, accuracy: %.4f' %
          (precision, recall, f1, accuracy))
