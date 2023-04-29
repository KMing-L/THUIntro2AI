import os

def test_lr():
    lrList = [0.0001, 0.001, 0.01, 0.1, 1]
    for lr in lrList:
        if not os.path.exists('results/result_CNN_bs16_lr%f_ep10_ml64.pickle' % lr):
            os.system('python src/main.py --model CNN --lr %f' % lr)
        if not os.path.exists('results/result_RNN_bs16_lr%f_ep10_ml64.pickle' % lr):
            os.system('python src/main.py --model RNN --lr %f' % lr)
        if not os.path.exists('results/result_MLP_bs16_lr%f_ep10_ml64.pickle' % lr):
            os.system('python src/main.py --model MLP --lr %f' % lr)

def test_batch_size():
    batchSizeList = [4, 8, 16, 32, 64, 128, 256, 512]
    for batchSize in batchSizeList:
        if not os.path.exists('results/result_CNN_bs%d_lr0.001000_ep10_ml64.pickle' % batchSize):
            os.system('python src/main.py --model CNN --batch_size %d' % batchSize)
        if not os.path.exists('results/result_RNN_bs%d_lr0.001000_ep10_ml64.pickle' % batchSize):
            os.system('python src/main.py --model RNN --batch_size %d' % batchSize)
        if not os.path.exists('results/result_MLP_bs%d_lr0.001000_ep10_ml64.pickle' % batchSize):
            os.system('python src/main.py --model MLP --batch_size %d' % batchSize)
        

def test_max_length():
    maxLengthList = [16, 32, 64, 128, 256]
    for maxLength in maxLengthList:
        if not os.path.exists('results/result_CNN_bs16_lr0.001000_ep10_ml%d.pickle' % maxLength):
            os.system('python src/main.py --model CNN --max_length %d' % maxLength)
        if not os.path.exists('results/result_RNN_bs16_lr0.001000_ep10_ml%d.pickle' % maxLength):
            os.system('python src/main.py --model RNN --max_length %d' % maxLength)
        if not os.path.exists('results/result_MLP_bs16_lr0.001000_ep10_ml%d.pickle' % maxLength):
            os.system('python src/main.py --model MLP --max_length %d' % maxLength)


def test_epoch():
    epochList = [5, 10, 15, 20]
    for epoch in epochList:
        if not os.path.exists('results/result_CNN_bs16_lr0.001000_ep%d_ml64.pickle' % epoch):
            os.system('python src/main.py --model CNN --epoch %d' % epoch)
        if not os.path.exists('results/result_RNN_bs16_lr0.001000_ep10_ml%d.pickle' % epoch):
            os.system('python src/main.py --model RNN --epoch %d' % epoch)
        if not os.path.exists('results/result_MLP_bs16_lr0.001000_ep10_ml%d.pickle' % epoch):
            os.system('python src/main.py --model MLP --epoch %d' % epoch)


def test_model():
    modelList = ['MLP', 'CNN', 'RNN']
    for model in modelList:
        if not os.path.exists('results/result_%s_bs16_lr0.001000_ep10_ml64.pickle' % model):
            os.system('python src/main.py --model %s' % model)

if __name__ == '__main__':
    test_lr()
    print('test_lr done')

    test_batch_size()
    print('test_batch_size done')

    test_max_length()
    print('test_max_length done')

    test_epoch()
    print('test_epoch down')
    
    test_model()
    print('test_model done')