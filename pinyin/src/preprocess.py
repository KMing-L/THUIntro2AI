import json
import os
import argparse
from process_raw_dataset import process_raw_word_pinyin, process_raw_sina_data
from config import *


def output_counts(ziyuan, force):
    if (not force) \
            and os.path.exists(WORD_COUNT) \
            and os.path.exists(FIRST_WORD_COUNT) \
            and ((ziyuan == 2 and os.path.exists(BINARY_WORD_COUNT)) or (ziyuan == 3 and os.path.exists(OPTIONAL_WORD_COUNT))):
        print('已经统计过字出现数量，跳过预处理过程。')
        return

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

    for month in SINA_MONTH:
        print('统计第', month, '月的字出现数量')
        for sentence in process_raw_sina_data(SINA_DATA % month):
            is_first = True
            for idx, word in enumerate(sentence[0]):
                if sentence[1][idx] == '*':
                    if word in may_new:
                        is_first = True
                    continue
                if word in words \
                    and sentence[1][idx] in pinyin2words \
                    and word in pinyin2words[sentence[1][idx]]:
                    this_word = word + sentence[1][idx]
                    count[this_word] = count.get(this_word, 0) + 1
                    if is_first:
                        first_count[this_word] = first_count.get(
                            this_word, 0) + 1
                        is_first = False
                    if ziyuan == 2:
                        if idx > 0 \
                                and sentence[0][idx - 1] in words \
                                and sentence[1][idx - 1] in pinyin2words \
                                and sentence[0][idx - 1] in pinyin2words[sentence[1][idx - 1]]:
                            last_word = sentence[0][idx - 1] + sentence[1][idx - 1]
                            if last_word not in binary_count:
                                binary_count[last_word] = {}
                            binary_count[last_word][this_word] = binary_count[last_word].get(
                                this_word, 0) + 1
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
                            if last_last_word not in optional_count:
                                optional_count[last_last_word] = {}
                            if last_word not in optional_count[last_last_word]:
                                optional_count[last_last_word][last_word] = {}
                            optional_count[last_last_word][last_word][this_word] = optional_count[last_last_word][last_word].get(
                                this_word, 0) + 1

    with open(WORD_COUNT, 'w', encoding='utf-8') as f:
        json.dump(count, f, ensure_ascii=False, indent=4)
    with open(FIRST_WORD_COUNT, 'w', encoding='utf-8') as f:
        json.dump(first_count, f, ensure_ascii=False, indent=4)
    if ziyuan == 2:
        with open(BINARY_WORD_COUNT, 'w', encoding='utf-8') as f:
            json.dump(binary_count, f, ensure_ascii=False, indent=4)
    elif ziyuan == 3:
        with open(OPTIONAL_WORD_COUNT, 'w', encoding='utf-8') as f:
            json.dump(optional_count, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='预处理字元模型')
    parser.add_argument('--ziyuan', type=int, default=2, help='字元模型的资源类型')
    parser.add_argument('-f', '--force', action='store_true', help='是否强制重新统计')
    args = parser.parse_args()

    output_counts(ziyuan=args.ziyuan, force=args.force)
