import torch
import torch.nn as nn
import torch.nn.functional as F
from data_reader import getWord2Id, getWord2Vec

word2id = getWord2Id()
word2vec = getWord2Vec(word2id)


class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.mlp_layer = nn.Linear(50, 128)
        self.dropout = nn.Dropout(0.4)
        self.relu = nn.ReLU()
        self.fc = nn.Linear(128, 2)

    def forward(self, sentence):
        embedding = self.embedding(sentence)                                          # B * len * 50
        out = self.relu(self.dropout(self.mlp_layer(embedding))).permute(0, 2, 1)     # B * 128 * len
        out = F.max_pool1d(out, out.shape[2]).squeeze(2)                              # B * 128
        return self.fc(out)                                                           # B * 2


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.cnn_layers = nn.ModuleList()
        self.cnn_layers.append(nn.Conv1d(50, 128, 3))
        self.cnn_layers.append(nn.Conv1d(50, 128, 5))
        self.cnn_layers.append(nn.Conv1d(50, 128, 7))
        self.relu = nn.ReLU()
        self.fc = nn.Linear(3 * 128, 2)

    def forward(self, sentence):
        embedding = self.embedding(sentence).permute(0, 2, 1)                       # B * 50 * len    
        conved = [self.relu(cnn_layer(embedding)) for cnn_layer in self.cnn_layers] # [B * 128 * (len - f + 1)]
        pooled = [F.max_pool1d(conv, conv.shape[2]).squeeze(2) for conv in conved]  # [B * 128]
        out = torch.cat(pooled, dim=1)                                              # B * (3 * 128)
        return self.fc(out)                                                         # B * 2


class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        self.embedding = nn.Embedding(len(word2id) + 1, 50)
        self.embedding.weight.data.copy_(torch.from_numpy(word2vec))
        self.embedding.weight.requires_grad = False
        self.encoder = nn.GRU(
            input_size=50, hidden_size=128, num_layers=2, bidirectional=True)
        self.decoder = nn.Linear(256, 64)
        self.relu = nn.ReLU()
        self.fc = nn.Linear(64, 2)

    def forward(self, sentence):
        embedding = self.embedding(sentence).permute(1, 0, 2)                               # len * B * 50

        h_0 = torch.rand(4, embedding.shape[1], 128)\
                   .to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))      # 4 * B * 128
        _, h_n = self.encoder(embedding, h_0)                                               # 4 * B * 128
        h_n = h_n.view(2, 2, -1, 128)                                                       # 2 * 2 * B * 128
        return self.fc(self.relu(self.decoder(torch.cat((h_n[-1,0], h_n[-1,1]), dim=-1))))  # B * 2
