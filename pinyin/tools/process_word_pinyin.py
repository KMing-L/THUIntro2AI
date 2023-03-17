# 请在项目根目录下执行此脚本

import json

words = []

with open('./datasets/一二级汉字表.txt', 'r', encoding='gbk') as f:
    words = list(f.readline())

json.dump(words, open('./data/words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
print(f'创建一二级汉字表 data/words.json, 共 {len(words)} 个')

pinyin = {}

num = 0
delete_num = 0

with open('./datasets/拼音汉字表.txt', 'r', encoding='gbk') as f:
    for line in f:
        line_words = line.split()
        for word in line_words[1:]:
            if word not in words:
                print('排除拼音汉字表中的非一二级词语: ', word)
                line_words.remove(word)
                delete_num += 1
        pinyin[line_words[0]] = line_words[1:]
        num += len(line_words[1:])

json.dump(pinyin, open('./data/pinyin2words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
print(f'创建拼音汉字对应表 data/pinyin2words.json, 共含 {num} 个汉字, 排除 {delete_num} 个非一二级词语')
