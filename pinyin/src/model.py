import argparse
import json
import math
from preprocess import output_counts
from config import *


class WordModel():
    def __init__(self, ziyuan=2):
        self.ziyuan = ziyuan
        output_counts(ziyuan=ziyuan, force=False)
        with open(WORD_TABLE, 'r', encoding='utf-8') as f:
            self.words = json.load(f)
        with open(PINYIN2WORDS_DICT, 'r', encoding='utf-8') as f:
            self.pinyin2words = json.load(f)
        with open(WORD_COUNT, 'r', encoding='utf-8') as f:
            self.count = json.load(f)
        with open(FIRST_WORD_COUNT, 'r', encoding='utf-8') as f:
            self.first_count = json.load(f)
        with open(BINARY_WORD_COUNT, 'r', encoding='utf-8') as f:
            self.binary_count = json.load(f)
        if ziyuan == 3:
            with open(OPTIONAL_WORD_COUNT, 'r', encoding='utf-8') as f:
                self.optional_count = json.load(f)

    def forward(self, pinyin):
        if self.ziyuan == 2:
            return self.__forward_binary(pinyin)
        elif self.ziyuan == 3:
            return self.__forward_optional(pinyin)
        else:
            print('ziyuan must be 2 or 3')
            return

    def __out_ans(self, f, last):
        min = float('inf')
        length = len(f)
        sentence = [''] * length
        for word in f[length - 1].keys():
            if f[length - 1][word] < min:
                min = f[length - 1][word]
                sentence[length - 1] = word
        for idx in range(length - 2, -1, -1):
            sentence[idx] = last[idx + 1][sentence[idx + 1]]
        return sentence

    def __forward_binary(self, pinyin):
        if len(pinyin) == 0:
            return []
        f = {}
        last = {}

        for idx, yin in enumerate(pinyin):
            f[idx] = dict.fromkeys(self.pinyin2words[yin], float('inf'))
            last[idx] = dict.fromkeys(self.pinyin2words[yin], '')
            for word in self.pinyin2words[yin]:
                this = word + yin
                if idx == 0:
                    f[idx][word] = 0
                else:
                    for last_word in f[idx - 1].keys():
                        last = last_word + pinyin[idx-1]
                        if self.count[last] > 0 and \
                                self.binary_count.get(last, {}).get(this, 0) > 0:
                            tmp = f[idx - 1][last_word] + math.log(
                                self.count[last]) - math.log(self.binary_count[last][this])
                            if tmp < f[idx][word]:
                                f[idx][word] = tmp
                                last[idx][word] = last_word
        return self.__out_ans(f, last)

    def __forward_optional(self, pinyin):
        if len(pinyin) == 0:
            return []
        f = {}
        last = {}

        for idx, yin in enumerate(pinyin):
            f[idx] = dict.fromkeys(self.pinyin2words[yin], float('inf'))
            last[idx] = dict.fromkeys(self.pinyin2words[yin], '')
            for word in self.pinyin2words[yin]:
                this = word + yin
                if idx == 0:
                    if self.count[yin][word] > 0 and self.first_count[yin][word] > 0:
                        f[idx][word] = math.log(
                            self.count[yin][word]) - math.log(self.first_count[yin][word])
                elif idx == 1:
                    for last_word in f[idx - 1].keys():
                        last = last_word + pinyin[idx-1]
                        if self.count[last] > 0 and \
                                self.binary_count.get(last, {}).get(this, 0) > 0:
                            tmp = f[idx - 1][last_word] + math.log(
                                self.count[last]) - math.log(self.binary_count[last][this])
                            if tmp < f[idx][word]:
                                f[idx][word] = tmp
                                last[idx][word] = last_word
                else:
                    for last_word in f[idx - 1].keys():
                        last = last_word + pinyin[idx-1]
                        for last_last_word in f[idx - 2].keys():
                            last_last = last_last_word + pinyin[idx-2]
                            if self.binary_count.get(last_last, {}).get(last, 0) > 0 and \
                                    self.optional_count.get(last_last, {}).get(last, {}).get(this, 0) > 0:
                                tmp = f[idx - 1][last_word] + math.log(self.binary_count[last_last][last]) - math.log(
                                    self.optional_count[last_last][last][this])
                                if tmp < f[idx][word]:
                                    f[idx][word] = tmp
                                    last[idx][word] = last_word
        return self.__out_ans(f, last)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ziyuan', type=int, default=2)
    args = parser.parse_args()
    model = WordModel(ziyuan=args.ziyuan)
    example = 'qing hua da xue shi shi jie yi liu da xue'
    pinyin = example.split(' ')
    print(model.forward(pinyin))
