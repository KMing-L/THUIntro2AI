import json
import os
import argparse
from process_raw_dataset import process_raw_word_pinyin, process_raw_sina_data, process_raw_smp_data, process_raw_baike_data
from config import *


def output_counts(ziyuan, month, data_from='sina'):
    process_raw_word_pinyin()

    with open(WORD_TABLE, 'r', encoding='utf-8') as f:
        words = json.load(f)
    with open(PINYIN2WORDS_DICT, 'r', encoding='utf-8') as f:
        pinyin2words = json.load(f)

    if data_from not in ['sina', 'smp', 'baike']:
        print('data_from must be sina or smp or baike')
        return

    count = {}
    binary_count = {}
    ternary_count = {}
    first_count = {}

    may_new = [' ', '‘', '“', '《', '》', '：', '；', '-']

    if data_from == 'sina':
        print('统计第', month, '月的字出现数量')
        iter = process_raw_sina_data(SINA_DATA % month)
    elif data_from == 'smp':
        iter = process_raw_smp_data()
    elif data_from == 'baike':
        iter = process_raw_baike_data()
    for sentence in iter:
        is_first = True
        for idx, word in enumerate(sentence[0]):
            if sentence[1][idx] == '*':
                if word in may_new:
                    is_first = True
                continue
            if len(sentence[1][idx]) == 3 and sentence[1][idx][1:] == 've':
                sentence[1][idx] = sentence[1][idx][0] + 'ue'
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
                        last_last_word = sentence[0][idx -
                                                     2] + sentence[1][idx - 2]
                        ternary = last_last_word + last_word + this_word
                        ternary_count[ternary] = ternary_count.get(
                            ternary, 0) + 1

    if data_from == 'sina':
        if ziyuan == 2:
            with open(WORD_CHILD % month, 'w', encoding='utf-8') as f:
                json.dump(count, f, ensure_ascii=False, indent=4)
            with open(FIRST_WORD_CHILD % month, 'w', encoding='utf-8') as f:
                json.dump(first_count, f, ensure_ascii=False, indent=4)
            with open(BINARY_WORD_CHILD % month, 'w', encoding='utf-8') as f:
                json.dump(binary_count, f, ensure_ascii=False, indent=4)
        elif ziyuan == 3:
            with open(TERNARY_WORD_CHILD % month, 'w', encoding='utf-8') as f:
                json.dump(ternary_count, f, ensure_ascii=False, indent=4)
    else:
        if ziyuan == 2:
            with open(WORD_COUNT % data_from, 'w', encoding='utf-8') as f:
                json.dump(count, f, ensure_ascii=False, indent=4)
            with open(FIRST_WORD_COUNT % data_from, 'w', encoding='utf-8') as f:
                json.dump(first_count, f, ensure_ascii=False, indent=4)
            with open(BINARY_WORD_COUNT % data_from, 'w', encoding='utf-8') as f:
                json.dump(binary_count, f, ensure_ascii=False, indent=4)
        elif ziyuan == 3:
            with open(TERNARY_WORD_COUNT % data_from, 'w', encoding='utf-8') as f:
                json.dump(ternary_count, f, ensure_ascii=False, indent=4)


def merge_all_sina(CHILD_PATH, PARENT_PATH):
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

    
def merge_all_data(PARENT_PATH):
    if not os.path.exists(PARENT_PATH % 'sina'):
        print('新浪数据的字出现数量未统计，跳过合并过程。')
        return
    if not os.path.exists(PARENT_PATH % 'smp'):
        print('smp数据的字出现数量未统计, 跳过合并过程。')
        return
    if not os.path.exists(PARENT_PATH % 'baike'):
        print('baike数据的字出现数量未统计, 跳过合并过程。')
        return
    count = {}
    for data_from in ['sina', 'smp', 'baike']:
        with open(PARENT_PATH % data_from, 'r', encoding='utf-8') as f:
            another = json.load(f)
            for key in another:
                count[key] = count.get(key, 0) + another[key]
    with open(PARENT_PATH % 'all', 'w', encoding='utf-8') as f:
        json.dump(count, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='预处理字元模型')
    parser.add_argument('--ziyuan', type=int, default=2, help='字元模型的资源类型')
    parser.add_argument('--month', type=int)
    parser.add_argument('--data_from', type=str, default='sina', help='数据来源')
    parser.add_argument('--all', action='store_true', help='同时统计三种资源的字元模型')
    args = parser.parse_args()

    if args.all:
        merge_all_data(WORD_COUNT)
        merge_all_data(FIRST_WORD_COUNT)
        merge_all_data(BINARY_WORD_COUNT)
        merge_all_data(TERNARY_WORD_COUNT)
    else:
        output_counts(ziyuan=args.ziyuan, month=args.month,
                    data_from=args.data_from)
        if args.data_from == 'sina':
            if args.ziyuan == 2:
                merge_all_sina(WORD_CHILD, WORD_COUNT)
                merge_all_sina(FIRST_WORD_CHILD, FIRST_WORD_COUNT)
                merge_all_sina(BINARY_WORD_CHILD, BINARY_WORD_COUNT)
            elif args.ziyuan == 3:
                merge_all_sina(TERNARY_WORD_CHILD, TERNARY_WORD_COUNT)
