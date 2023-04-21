import torch
import torch.nn as nn
import torch.nn.functional as F
from data_reader import getWord2Id, getWord2Vec

word2id = getWord2Id()
word2vec = getWord2Vec(word2id)


class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.embedding = nn.Embedding(len(word2id), 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.relu = nn.ReLU()
        self.hidden = nn.Linear(50, 100)
        self.out = nn.Linear(100, 2)
        nn.init.normal_(self.hidden.weight, mean=0, std=0.01)
        nn.init.normal_(self.out.weight, mean=0, std=0.01)

    def forward(self, sentence):
        embedding = self.embedding(sentence)
        out = self.relu(self.hidden(embedding)).permute(0, 2, 1)
        out = F.max_pool1d(out, out.size(2)).squeeze(2)
        return self.out(out)
