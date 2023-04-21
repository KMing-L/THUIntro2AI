import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from data_reader import getWord2Id, getData
from model import MLP
from typing import Tuple
from tqdm import tqdm


def getDataLoader(batch_size: int) -> Tuple[DataLoader, DataLoader, DataLoader]:
    word2id = getWord2Id()
    train_contents, train_labels = getData('dataset/train.txt', word2id)
    test_contents, test_labels = getData('dataset/test.txt', word2id)
    val_contents, val_labels = getData('dataset/validation.txt', word2id)
    train_dataset = TensorDataset(torch.from_numpy(train_contents).type(torch.int32),
                                  torch.from_numpy(train_labels).type(torch.long))
    test_dataset = TensorDataset(torch.from_numpy(test_contents).type(torch.int32),
                                 torch.from_numpy(test_labels).type(torch.long))
    val_dataset = TensorDataset(torch.from_numpy(val_contents).type(torch.int32),
                                torch.from_numpy(val_labels).type(torch.long))
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    return train_loader, test_loader, val_loader


def test(model, data_loader):
    model.eval()
    TP, FP, FN = 0, 0, 0
    t = tqdm(data_loader)
    for batch in t:
        t.set_description('Test: Epoch %d' % epoch)
        label = batch[1].to(DEVICE)
        output = model(batch[0].to(DEVICE))
        # print(output[:20])
        TP += ((output.argmax(1) == 1) & (label == 1)).sum().item()
        FP += ((output.argmax(1) == 1) & (label == 0)).sum().item()
        FN += ((output.argmax(1) == 0) & (label == 1)).sum().item()
    print('TP: %d, FP: %d, FN: %d' % (TP, FP, FN))
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def train(model, optimizer, loss, train_loader, epoch, val_loader):
    model.train()
    t = tqdm(train_loader)
    for batch in t:
        t.set_description('Train: Epoch %d' % epoch)
        optimizer.zero_grad()
        label = batch[1].to(DEVICE)
        output = model(batch[0].to(DEVICE))
        l = loss(output, label)
        t.set_postfix(l=l.item())
        l.backward()
        optimizer.step()
    return test(model, val_loader)


if __name__ == '__main__':
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    lr = 1e-3
    epoch = 10
    batch_size = 64
    train_loader, test_loader, val_loader = getDataLoader(batch_size)
    model = MLP().to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss = nn.CrossEntropyLoss()
    best_f1 = 0.0

    path_checkpoint = 'save_model/checkpoint.pkl'

    for e in range(epoch):
        val_precision, val_recall, val_f1 = train(
            model, optimizer, loss, train_loader, e, val_loader)
        print('Epoch %d: Val Precision: %.4f, Val Recall: %.4f, Val F1: %.4f' %
              (e, val_precision, val_recall, val_f1))
        if val_f1 > best_f1:
            best_f1 = val_f1
            checkpoint = {
                'model': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'epoch': e,
                'best_f1': best_f1
            }
            torch.save(checkpoint, path_checkpoint)

    checkpoint = torch.load(path_checkpoint)
    model.load_state_dict(checkpoint['model'])
    print('Best Epoch: %d' % checkpoint['epoch'])
    print('Validation F1: %.4f' % checkpoint['best_f1'])
    test_precision, test_recall, test_f1 = test(model, test_loader)
    print('Test Precision: %.4f, Test Recall: %.4f, Test F1: %.4f' %
          (test_precision, test_recall, test_f1))
