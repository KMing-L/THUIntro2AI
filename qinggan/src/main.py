import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from data_reader import getWord2Id, getData
from model import *
from typing import Tuple
from tqdm import tqdm
import argparse
import pickle


def argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='MLP')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=0.01)
    parser.add_argument('--epoch', type=int, default=10)
    parser.add_argument('--max_length', type=int, default=64)
    return parser.parse_args()


def getDataLoader(batch_size: int, max_length: int) -> Tuple[DataLoader, DataLoader, DataLoader]:
    word2id = getWord2Id()
    train_contents, train_labels = getData(
        'dataset/train.txt', word2id, max_length)
    test_contents, test_labels = getData(
        'dataset/test.txt', word2id, max_length)
    val_contents, val_labels = getData(
        'dataset/validation.txt', word2id, max_length)
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


def test(model, data_loader, loss=None, is_val=False) -> Tuple[float, float, float, float]:
    model.eval()
    TP, FP, FN, TN = 0, 0, 0, 0
    t = tqdm(data_loader)
    label_all = torch.empty(0, dtype=torch.long)
    out_all = torch.empty((0, 2), dtype=torch.float)
    for batch in t:
        t.set_description('Test: Epoch %d' % epoch)
        label = batch[1].to(DEVICE)
        output = model(batch[0].to(DEVICE))
        if is_val:
            label_all = torch.cat((label_all, label.cpu()), 0)
            out_all = torch.cat((out_all, output.cpu()), 0)
        TP += ((output.argmax(1) == 1) & (label == 1)).sum().item()
        FP += ((output.argmax(1) == 1) & (label == 0)).sum().item()
        FN += ((output.argmax(1) == 0) & (label == 1)).sum().item()
        TN += ((output.argmax(1) == 0) & (label == 0)).sum().item()
    if is_val:
        loss_val.append(loss(out_all, label_all).item())
    precision = TP / (TP + FP) if TP + FP != 0 else 0
    recall = TP / (TP + FN) if TP + FN != 0 else 0
    f1 = 2 * precision * recall / \
        (precision + recall) if precision + recall != 0 else 0
    accuracy = (TP + TN) / (TP + FP + FN + TN) if TP + FP + FN + TN != 0 else 0
    return precision, recall, f1, accuracy


def train(model, optimizer, loss, train_loader, epoch, val_loader) -> Tuple[float, float, float, float]:
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
        loss_train.append(l.item())
    return test(model, val_loader, loss, True)


if __name__ == '__main__':
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args = argparser()
    batch_size = args.batch_size
    lr = args.lr
    epoch = args.epoch
    max_length = args.max_length
    train_loader, test_loader, val_loader = getDataLoader(
        batch_size, max_length)
    if args.model == 'MLP':
        model = MLP().to(DEVICE)
    elif args.model == 'CNN':
        model = CNN().to(DEVICE)
    elif args.model == 'RNN':
        model = RNN().to(DEVICE)
    else:
        raise ValueError('Invalid model name')

    loss_train = []
    loss_val = []

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=3, gamma=0.1)
    loss = nn.CrossEntropyLoss()
    best_acc = 0.0

    path_checkpoint = 'saved/checkpoint_%s_bs%d_lr%f_ep%d_ml%d.pkl' % (
        args.model, batch_size, lr, epoch, max_length)

    for e in range(epoch):
        val_precision, val_recall, val_f1, val_acc = train(
            model, optimizer, loss, train_loader, e, val_loader)
        scheduler.step()
        print('Epoch: %d, Validation Precision: %.4f, Validation Recall: %.4f, Validation F1: %.4f, Validation Accuracy: %.4f' %
              (e, val_precision, val_recall, val_f1, val_acc))
        if val_f1 > best_acc:
            best_acc = val_f1
            checkpoint = {
                'model': model.state_dict(),
                'optimizer': optimizer.state_dict(),
                'epoch': e
            }
            torch.save(checkpoint, path_checkpoint)

    checkpoint = torch.load(path_checkpoint)
    model.load_state_dict(checkpoint['model'])
    print('Best Epoch: %d' % checkpoint['epoch'])
    test_precision, test_recall, test_f1, test_acc = test(model, test_loader)
    print('Test Precision: %.4f, Test Recall: %.4f, Test F1: %.4f, Test Accuracy: %.4f' %
          (test_precision, test_recall, test_f1, test_acc))

    path_save = 'results/result_%s_bs%d_lr%f_ep%d_ml%d.pickle' % (
        args.model, batch_size, lr, epoch, max_length)
    with open(path_save, 'wb') as f:
        pickle.dump({'accuracy': test_acc, 'f1': test_f1,
                    'train_loss': loss_train, 'val_loss': loss_val}, f)
