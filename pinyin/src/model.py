import argparse
import json
import math
from config import *


class WordModel():
    def __init__(self, ziyuan=2, data_from='sina', alpha=0.9999, beta=0.95):
        self.ziyuan = ziyuan
        with open(WORD_TABLE, 'r', encoding='utf-8') as f:
            self.words = json.load(f)
        with open(PINYIN2WORDS_DICT, 'r', encoding='utf-8') as f:
            self.pinyin2words = json.load(f)
        with open(WORD_COUNT % data_from, 'r', encoding='utf-8') as f:
            self.count = json.load(f)
        with open(FIRST_WORD_COUNT % data_from, 'r', encoding='utf-8') as f:
            self.first_count = json.load(f)
        with open(BINARY_WORD_COUNT % data_from, 'r', encoding='utf-8') as f:
            self.binary_count = json.load(f)
        if ziyuan == 3:
            with open(TERNARY_WORD_COUNT % data_from, 'r', encoding='utf-8') as f:
                self.ternary_count = json.load(f)
        if data_from == 'sina':
            self.all_word = sina_all_word
        elif data_from == 'smp':
            self.all_word = smp_all_word
        elif data_from == 'baike':
            self.all_word = baike_all_word
        else:
            self.all_word = all_all_word
        self.alpha = alpha
        self.beta = beta
    
    def set(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    def forward(self, pinyin):
        if self.ziyuan == 2:
            return self.__forward_binary(pinyin)
        elif self.ziyuan == 3:
            return self.__forward_ternary(pinyin)
        else:
            print('ziyuan must be 2 or 3')
            return

    def __forward_binary(self, pinyin):
        if len(pinyin) == 0:
            return []
        f = [{} for _ in range(len(pinyin))]
        l = [{} for _ in range(len(pinyin))]

        for word in self.pinyin2words[pinyin[0]]:
            this = word + pinyin[0]
            if this not in self.first_count:
                continue
            f[0][this] = -math.log(self.first_count[this])
            l[0][this] = ''

        for i in range(1, len(pinyin)):
            for last in f[i-1].keys():
                for word in self.pinyin2words[pinyin[i]]:
                    this = word + pinyin[i]
                    if this not in self.count:
                        continue
                    P = self.alpha * self.binary_count.get(last + this, 0) / self.count[last] + (
                        1-self.alpha) * self.count[this] / self.all_word
                    if this not in f[i] or f[i][this] > f[i-1][last] - math.log(P):
                        f[i][this] = f[i-1][last] - math.log(P)
                        l[i][this] = last

        max_p = float('inf')
        max_w = ''
        for word in f[-1].keys():
            if f[-1][word] < max_p:
                max_p = f[-1][word]
                max_w = word
        if max_w == '':
            return '*' * len(pinyin)
        ans = ''
        this = max_w
        for i in range(len(f)-1, -1, -1):
            ans = this[0] + ans
            this = l[i][this]
        return ans

    def __forward_ternary(self, pinyin):
        if len(pinyin) == 0:
            return []
        f = [{} for _ in range(len(pinyin)-1)]
        l = [{} for _ in range(len(pinyin)-1)]

        for word in self.pinyin2words[pinyin[0]]:
            this = word + pinyin[0]
            if this not in self.first_count:
                continue
            f[0][this] = {}
            l[0][this] = {}
            if len(pinyin) == 1:
                continue
            for next_word in self.pinyin2words[pinyin[1]]:
                next = next_word + pinyin[1]
                if next not in self.count:
                    continue
                P = self.alpha * self.binary_count.get(this+next, 0) / self.count[this] + (
                    1-self.alpha) * self.count[next] / self.all_word
                f[0][this][next] = -math.log(
                    P) - math.log(self.first_count[this])
                l[0][this][next] = ''

        for i in range(len(pinyin)-2):
            for last_last in f[i].keys():
                for last in f[i][last_last].keys():
                    for word in self.pinyin2words[pinyin[i+2]]:
                        this = word + pinyin[i+2]
                        if this not in self.count:
                            continue
                        P = self.beta * self.ternary_count.get(last_last+last+this, 0) / self.binary_count.get(last_last+last, 1) + (1-self.beta) * (
                            self.alpha * self.binary_count.get(last+this, 0) / self.count[last] + (1-self.alpha) * self.count[this] / self.all_word)
                        if last not in f[i+1]:
                            f[i+1][last] = {}
                            l[i+1][last] = {}
                        if P < 1e-10:
                            continue
                        if this not in f[i+1][last] or f[i+1][last][this] > f[i][last_last][last] - math.log(P):
                            if not P:
                                f[i+1][last][this] = float('-inf')
                            else:    
                                f[i+1][last][this] = f[i][last_last][last] - \
                                    math.log(P)
                            l[i+1][last][this] = last_last

        max_w = ''
        max_second_w = ''
        max_p = float('inf')
        for word in f[-1].keys():
            for second_word in f[-1][word].keys():
                if f[-1][word][second_word] < max_p:
                    max_p = f[-1][word][second_word]
                    max_w = word
                    max_second_w = second_word
        if max_second_w == '':
            return '*' * len(pinyin)
        ans = max_second_w[0]
        this = max_w
        next = max_second_w
        for i in range(len(f)-1, -1, -1):
            ans = this[0] + ans
            this, next = l[i][this][next], this
        return ans


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ziyuan', type=int, default=2)
    parser.add_argument('-d', '--data_from', type=str, default='sina')
    args = parser.parse_args()
    model = WordModel(ziyuan=args.ziyuan, data_from=args.data_from)
    example = 'qing hua da xue shi shi jie yi liu da xue'
    pinyin = example.split(' ')
    print(model.forward(pinyin))
