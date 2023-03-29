# 请在项目根目录下执行此脚本

from config import *
import json
import os
from pypinyin import lazy_pinyin, Style


def process_raw_word_pinyin():
    words = []

    with open(LEGAL_WORDS, 'r', encoding='gbk') as f:
        words = list(f.readline())

    if os.path.exists(WORD_TABLE):
        print('一二级汉字表' + WORD_TABLE + '已存在')
    else:
        with open(WORD_TABLE, 'r', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=4)
        print(f'创建一二级汉字表 {WORD_TABLE}, 共 {len(words)} 个')

    if os.path.exists(PINYIN2WORDS_DICT):
        print('拼音汉字对应表' + PINYIN2WORDS_DICT + '已存在')
    else:
        pinyin = {}

        num = 0
        delete_num = 0

        with open(PINYIN2WORDS_RAW, 'r', encoding='gbk') as f:
            for line in f:
                line_words = line.split()
                for word in line_words[1:]:
                    if word not in words:
                        print('排除拼音汉字表中的非一二级词语: ', word)
                        line_words.remove(word)
                        delete_num += 1
                pinyin[line_words[0]] = line_words[1:]
                num += len(line_words[1:])
        with open(PINYIN2WORDS_DICT, 'w', encoding='utf-8') as f:
            json.dump(pinyin, f, ensure_ascii=False, indent=4)
        print(
            f'创建拼音汉字对应表 {PINYIN2WORDS_DICT}, 共含 {num} 个汉字, 排除 {delete_num} 个非一二级词语')


def process_raw_sina_data(path):
    with open(path, 'r', encoding='gbk') as f:
        items = f.readlines()
        for item in items:
            item_dict = json.loads(item)
            item_pinyin = lazy_pinyin(item_dict['title'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['title'], item_pinyin)
            item_pinyin = lazy_pinyin(item_dict['html'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['html'], item_pinyin)


def process_raw_smp_data():
    with open(SMP_DATA, 'r', encoding='gbk') as f:
        items = f.readlines()
        for item in items:
            item_dict = eval(item)
            item_pinyin = lazy_pinyin(item_dict['content'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['content'], item_pinyin)


def process_raw_baike_data():
    with open(BAIKE_DATA, 'r', encoding='utf-8') as f:
        items = f.readlines()
        for item in items:
            item_dict = json.loads(item)
            item_pinyin = lazy_pinyin(item_dict['category'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['category'], item_pinyin)
            item_pinyin = lazy_pinyin(item_dict['title'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['title'], item_pinyin)
            item_pinyin = lazy_pinyin(item_dict['desc'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['desc'], item_pinyin)
            item_pinyin = lazy_pinyin(item_dict['answer'], style=Style.NORMAL, errors=lambda item: [
                                      '*' for i in range(len(item))])
            yield (item_dict['answer'], item_pinyin)


if __name__ == '__main__':
    process_raw_word_pinyin()
    process_raw_sina_data()
