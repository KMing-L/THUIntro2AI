import torch
import torch.nn as nn
import torch.nn.functional as F
from data_reader import getWord2Id, getWord2Vec
from transformers import BertModel

word2id = getWord2Id()
word2vec = getWord2Vec(word2id)


class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
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


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.conv1 = nn.Conv2d(1, 20, (3, 50))
        self.conv2 = nn.Conv2d(1, 20, (5, 50))
        self.conv3 = nn.Conv2d(1, 20, (7, 50))
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(60, 2)

    @staticmethod
    def conv_and_pool(x, conv):
        x = conv(x)
        x = F.relu(x.squeeze(3))
        x = F.max_pool1d(x, x.size(2)).squeeze(2)
        return x
    
    def forward(self, sentence):
        x = self.embedding(sentence).unsqueeze(1)
        x1 = self.conv_and_pool(x, self.conv1)
        x2 = self.conv_and_pool(x, self.conv2)
        x3 = self.conv_and_pool(x, self.conv3)
        x = torch.cat((x1, x2, x3), 1)
        x = self.dropout(x)
        return F.log_softmax(self.fc(x), dim=1)


class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.encoder = nn.LSTM(
            input_size=50,
            hidden_size=100,
            num_layers=2,
            bidirectional=True,
        )
        self.decoder = nn.Linear(200, 64)
        self.fc = nn.Linear(64, 2)
    
    def forward(self, sentence):
        embedding = self.embedding(sentence)
        _, (h_n, _) = self.encoder(embedding.permute(1, 0, 2))
        h_n = h_n.view(2, 2, -1, 100)
        return self.fc(self.decoder(torch.cat((h_n[-1, 0], h_n[-1, 1]), dim=-1)))
