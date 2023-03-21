import json
import os
import argparse
from process_raw_dataset import process_raw_word_pinyin, process_raw_sina_data
from config import *


def output_counts(ziyuan, month):
    process_raw_word_pinyin()

    with open(WORD_TABLE, 'r', encoding='utf-8') as f:
        words = json.load(f)
    with open(PINYIN2WORDS_DICT, 'r', encoding='utf-8') as f:
        pinyin2words = json.load(f)

    count = {}
    binary_count = {}
    optional_count = {}
    first_count = {}

    may_new = [' ', '‘', '“', '《', '》', '：', '；', '-']

    print('统计第', month, '月的字出现数量')
    for sentence in process_raw_sina_data(SINA_DATA % month):
        is_first = True
        for idx, word in enumerate(sentence[0]):
            if sentence[1][idx] == '*':
                if word in may_new:
                    is_first = True
                continue
            if len(sentence[1][idx])==3 and sentence[1:]=='ve':
                sentence[1][idx] = sentence[0] + 'ue'
            if word in words \
                and sentence[1][idx] in pinyin2words \
                and word in pinyin2words[sentence[1][idx]]:
                this_word = word + sentence[1][idx]
                count[this_word] = count.get(this_word, 0) + 1
                if ziyuan == 2:
                    if is_first:
                        first_count[this_word] = first_count.get(
                            this_word, 0) + 1
                        is_first = False
                    if idx > 0 \
                            and sentence[0][idx - 1] in words \
                            and sentence[1][idx - 1] in pinyin2words \
                            and sentence[0][idx - 1] in pinyin2words[sentence[1][idx - 1]]:
                        last_word = sentence[0][idx - 1] + sentence[1][idx - 1]
                        binary = last_word + this_word
                        binary_count[binary] = binary_count.get(binary, 0) + 1
                elif ziyuan == 3:
                    if idx > 1 \
                            and sentence[0][idx - 1] in words \
                            and sentence[1][idx - 1] in pinyin2words \
                            and sentence[0][idx - 1] in pinyin2words[sentence[1][idx - 1]] \
                            and sentence[0][idx - 2] in words \
                            and sentence[1][idx - 2] in pinyin2words \
                            and sentence[0][idx - 2] in pinyin2words[sentence[1][idx - 2]]:
                        last_word = sentence[0][idx - 1] + sentence[1][idx - 1]
                        last_last_word = sentence[0][idx - 2] + sentence[1][idx - 2]
                        optional = last_last_word + last_word + this_word
                        optional_count[optional] = optional_count.get(optional, 0) + 1

    if ziyuan == 2:
        with open(WORD_CHILD, 'w', encoding='utf-8') as f:
            json.dump(count, f, ensure_ascii=False, indent=4)
        with open(FIRST_WORD_CHILD, 'w', encoding='utf-8') as f:
            json.dump(first_count, f, ensure_ascii=False, indent=4)
        with open(BINARY_WORD_CHILD, 'w', encoding='utf-8') as f:
            json.dump(binary_count, f, ensure_ascii=False, indent=4)
    elif ziyuan == 3:
        with open(OPTIONAL_WORD_CHILD % month, 'w', encoding='utf-8') as f:
            json.dump(optional_count, f, ensure_ascii=False, indent=4)


def merge_all(CHILD_PATH, PARENT_PATH):
    for month in SINA_MONTH:
        if not os.path.exists(CHILD_PATH % month):
            print('第', month, '月的字出现数量未统计，跳过合并过程。')
            return
    count = {}
    for month in SINA_MONTH:
        with open(CHILD_PATH % month, 'r', encoding='utf-8') as f:
            another = json.load(f)
            for key in another:
                count[key] = count.get(key, 0) + another[key]
    with open(PARENT_PATH, 'w', encoding='utf-8') as f:
        json.dump(count, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='预处理字元模型')
    parser.add_argument('--ziyuan', type=int, default=2, help='字元模型的资源类型')
    parser.add_argument('--month', type=int)
    args = parser.parse_args()

    output_counts(ziyuan=args.ziyuan, mon=args.month)

    if args.ziyuan==2:
        merge_all(WORD_CHILD, WORD_COUNT)
        merge_all(FIRST_WORD_CHILD, FIRST_WORD_COUNT)
        merge_all(BINARY_WORD_CHILD, BINARY_WORD_COUNT)
    elif args.ziyuan==3:
        merge_all(OPTIONAL_WORD_CHILD, OPTIONAL_WORD_COUNT)