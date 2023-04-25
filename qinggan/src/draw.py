import pickle
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import json


def drawAccF1(iter, change_str, read_path):
    CNN_results = []
    RNN_results = []
    MLP_results = []
    for it in iter:
        with open(read_path % ('CNN', it), 'rb') as f:
            CNN_results.append(pickle.load(f))
        with open(read_path % ('RNN', it), 'rb') as f:
            RNN_results.append(pickle.load(f))
        with open(read_path % ('MLP', it), 'rb') as f:
            MLP_results.append(pickle.load(f))
    CNN_acc = [round(CNN_results[i]['accuracy'], 2) for i in range(len(iter))]
    CNN_f1 = [round(CNN_results[i]['f1'], 2) for i in range(len(iter))]
    RNN_acc = [round(RNN_results[i]['accuracy'], 2) for i in range(len(iter))]
    RNN_f1 = [round(RNN_results[i]['f1'], 2) for i in range(len(iter))]
    MLP_acc = [round(MLP_results[i]['accuracy'], 2) for i in range(len(iter))]
    MLP_f1 = [round(MLP_results[i]['f1'], 2) for i in range(len(iter))]

    acc_data = {change_str: [str(it) for it in iter],
                'CNN': CNN_acc, 'RNN': RNN_acc, 'MLP': MLP_acc}
    acc_df = pd.DataFrame(acc_data)
    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x=change_str, y="MLP", data=acc_df, label="MLP")
    sns.lineplot(x=change_str, y="CNN", data=acc_df, label="CNN")
    sns.lineplot(x=change_str, y="RNN", data=acc_df, label="RNN")
    plt.title(f"Accuracy by {change_str} Of Different Models")
    plt.xlabel(change_str)
    plt.ylabel("Accuracy")
    plt.legend()
    plt.savefig(f'images/{change_str}_acc.png')

    f1_data = {change_str: [str(it) for it in iter],
               'CNN': CNN_f1, 'RNN': RNN_f1, 'MLP': MLP_f1}
    f1_df = pd.DataFrame(f1_data)
    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x=change_str, y="MLP", data=f1_df, label="MLP")
    sns.lineplot(x=change_str, y="CNN", data=f1_df, label="CNN")
    sns.lineplot(x=change_str, y="RNN", data=f1_df, label="RNN")
    plt.title(f"F1 Score by {change_str} Of Different Models")
    plt.xlabel(change_str)
    plt.ylabel("F1 Score")
    plt.legend()
    plt.savefig(f'images/{change_str}_f1.png')


def drawLoss():
    read_path = 'results/result_%s_bs16_lr0.010000_ep10_ml64.pickle'
    with open(read_path % ('CNN'), 'rb') as f:
        CNN_result = pickle.load(f)
    with open(read_path % ('RNN'), 'rb') as f:
        RNN_result = pickle.load(f)
    with open(read_path % ('MLP'), 'rb') as f:
        MLP_result = pickle.load(f)

    train_data = {'Step': [i for i in range(1, len(CNN_result['train_loss']) + 1)], 'CNN_train_loss': CNN_result['train_loss'], 'RNN_train_loss': RNN_result['train_loss'], 'MLP_train_loss': MLP_result['train_loss']}
    train_df = pd.DataFrame(train_data)
    batch_every_epoch = len(CNN_result['train_loss']) // 10
    val_data = {'Epoch': [i for i in range(batch_every_epoch, len(CNN_result['train_loss']) + 1, batch_every_epoch)],
                'CNN_val_loss': CNN_result['val_loss'], 'RNN_val_loss': RNN_result['val_loss'], 'MLP_val_loss': MLP_result['val_loss']}
    val_df = pd.DataFrame(val_data)

    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x='Step', y='MLP_train_loss', data=train_df, label="MLP Train Loss")
    sns.lineplot(x='Epoch', y='MLP_val_loss', data=val_df, label="MLP Val Loss")
    plt.title("Loss of MLP while Training")
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.legend()
    plt.savefig('images/MLP_loss.png')

    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x='Step', y='CNN_train_loss', data=train_df, label="CNN Train Loss")
    sns.lineplot(x='Epoch', y='CNN_val_loss', data=val_df, label="CNN Val Loss")
    plt.title("Loss of CNN while Training")
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.legend()
    plt.savefig('images/CNN_loss.png')

    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x='Step', y='RNN_train_loss', data=train_df, label="RNN Train Loss")
    sns.lineplot(x='Epoch', y='RNN_val_loss', data=val_df, label="RNN Val Loss")
    plt.title("Loss of RNN while Training")
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.legend()
    plt.savefig('images/RNN_loss.png')


def drawModelACCF1():
    read_path = 'results/result_%s_bs16_lr0.010000_ep10_ml64.pickle'
    with open(read_path % ('CNN'), 'rb') as f:
        CNN_result = pickle.load(f)
    with open(read_path % ('RNN'), 'rb') as f:
        RNN_result = pickle.load(f)
    with open(read_path % ('MLP'), 'rb') as f:
        MLP_result = pickle.load(f)
    models = ['MLP', 'CNN', 'RNN', 'BERT']
    acc = [MLP_result['accuracy'], CNN_result['accuracy'], RNN_result['accuracy'], 0.90]
    f1 = [MLP_result['f1'], CNN_result['f1'], RNN_result['f1'], 0.90]
    data = {'Model': models, 'Accuracy': acc, 'F1 Score': f1}
    df = pd.DataFrame(data)
    plt.cla()
    sns.set(style='whitegrid')
    sns.scatterplot(x='Accuracy', y='F1 Score', data=df, hue='Model')
    plt.title("Accuracy and F1 Score of Different Models")
    plt.xlabel("Accuracy")
    plt.ylabel("F1 Score")
    plt.legend()
    plt.savefig('images/Model_acc_f1.png')


def drawBertLoss():
    with open('saved/checkpoint-3500/trainer_state.json', 'r') as f:
        bert_result = json.load(f)
    steps = [str(bert_result['log_history'][i]['step']) for i in range(len(bert_result['log_history']))]
    train_loss = [bert_result['log_history'][i]['loss'] for i in range(len(bert_result['log_history']))]
    data = {'Step': steps, 'Train Loss': train_loss}
    df = pd.DataFrame(data)
    plt.cla()
    sns.set(style='whitegrid')
    sns.lineplot(x='Step', y='Train Loss', data=df, label="BERT Train Loss")
    plt.title("Loss of BERT while Training")
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.legend()
    plt.savefig('images/BERT_loss.png')


if __name__ == '__main__':
    drawAccF1([0.0001, 0.001, 0.01, 0.1, 1], 'Learning Rate',
              'results/result_%s_bs16_lr%f_ep10_ml64.pickle')
    drawAccF1([4, 8, 16, 32, 64, 128, 256], 'Batch Size',
              'results/result_%s_bs%d_lr0.010000_ep10_ml64.pickle')
    drawAccF1([16, 32, 64, 128, 256], 'Sentence Max Length',
              'results/result_%s_bs16_lr0.010000_ep10_ml%d.pickle')
    drawLoss()
    drawModelACCF1()
    drawBertLoss()
