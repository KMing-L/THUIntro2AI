import json
from process_raw_dataset import process_raw_word_pinyin, process_raw_sina_data
from config import *

def output_counts():
    process_raw_word_pinyin()

    with open(WORD_TABLE, 'r', encoding='utf-8') as f:
        words = json.load(f)
    with open(PINYIN2WORDS_DICT, 'r', encoding='utf-8') as f:
        pinyin2words = json.load(f)

    count = dict.fromkeys(pinyin2words, {})
    for pinyin in count:
        count[pinyin] = dict.fromkeys(pinyin2words[pinyin], 0)

    binary_count = {}
    first_count = count.copy()

    may_new = [' ', '‘', '“', '《', '》', '：', '；', '-']

    f = open('error.txt', 'a', encoding='utf-8')

    for month in SINA_MONTH:
        print('统计第', month, '月的字出现数量')
        for sentence in process_raw_sina_data(SINA_DATA % month):
            is_first = True
            for idx, word in enumerate(sentence[0]):
                if sentence[1][idx] == '*':
                    if word in may_new:
                        is_first = True
                    continue
                if word in words:
                    try:
                        count[sentence[1][idx]][word] += 1
                    except KeyError:
                        if len(sentence[1][idx]) == 3 and sentence[1][idx][1] == 'v' and sentence[1][idx][2] == 'e':
                            sentence[1][idx] = sentence[1][idx][0] + 'ue'
                        elif sentence[1][idx] == 'nei' and word == '哪':
                            sentence[1][idx] = 'na'
                        elif sentence[1][idx] == 'wen' and word == '免':
                            sentence[1][idx] = 'mian'
                        elif sentence[1][idx] == 'hang' and word == '珩':
                            sentence[1][idx] = 'heng'
                        elif sentence[1][idx] == 'n' and word == '嗯':
                            sentence[1][idx] = 'en'
                        elif sentence[1][idx] == 'xin' and word == '寻':
                            sentence[1][idx] = 'xun'
                        elif sentence[1][idx] == 'die' and word == '嗲':
                            sentence[1][idx] = 'dia'
                        elif sentence[1][idx] == 'gua' and word == '聒':
                            sentence[1][idx] = 'guo'
                        elif sentence[1][idx] == 'shi' and word == '豉':
                            sentence[1][idx] = 'chi'
                        elif sentence[1][idx] == 'pang' and word == '房':
                            sentence[1][idx] = 'fang'
                        elif sentence[1][idx] == 'ma' and word == '嬷':
                            sentence[1][idx] = 'mo'
                        elif sentence[1][idx] == 'ji' and word == '齐':
                            sentence[1][idx] = 'qi'
                        elif sentence[1][idx] == 'gun' and word == '混':
                            sentence[1][idx] = 'hun'
                        elif sentence[1][idx] == 'de' and word == '登':
                            sentence[1][idx] = 'deng'
                        elif sentence[1][idx] == 'bo' and word == '蕃':
                            sentence[1][idx] = 'fan'
                        try:
                            count[sentence[1][idx]][word] += 1
                        except KeyError:
                            f.write('KeyError: ' + sentence[1][idx] + ' ' + word + '\n')
                            f.write(sentence[0][idx - 1] + ' ' + sentence[0][idx] + ' ' + sentence[0][idx + 1] + '\n')
                    if is_first:
                        try:
                            first_count[sentence[1][idx]][word] += 1
                        except KeyError:
                            f.write('KeyError: ' + sentence[1][idx] + ' ' + word + '\n')
                            f.write(sentence[0][idx - 1] + ' ' + sentence[0][idx] + ' ' + sentence[0][idx + 1] + '\n')
                        is_first = False
                    if idx < len(sentence[0]) - 1 and sentence[0][idx + 1] in words:
                        if word not in binary_count:
                            binary_count[word] = {}
                        binary_count[word][sentence[0][idx + 1]] = binary_count[word].get(sentence[0][idx + 1], 0) + 1


    with open(WORD_COUNT, 'w', encoding='utf-8') as f:
        json.dump(count, f, ensure_ascii=False, indent=4)
    with open(BINARY_WORD_COUNT, 'w', encoding='utf-8') as f:
        json.dump(binary_count, f, ensure_ascii=False, indent=4)
    with open(FIRST_WORD_COUNT, 'w', encoding='utf-8') as f:
        json.dump(first_count, f, ensure_ascii=False, indent=4)
                    
if __name__ == '__main__':
    output_counts()