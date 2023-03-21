import argparse
import sys
from model import WordModel

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ziyuan', type=int, default=2, help='字元模型的字元数')
    parser.add_argument('-t', '--test', action='store_true', help='测试模式')
    parser.add_argument('-i', '--input', type=str, help='测试输入文件')
    parser.add_argument('-o', '--output', type=str, help='测试输出文件')
    parser.add_argument('-a', '--answer', type=str, help='测试答案文件')
    args = parser.parse_args()
    model = WordModel(ziyuan=args.ziyuan)

    lines = []
    sentences = []
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    if args.test:
        if (len(lines)==0) or not args.output or not args.answer:
            print('测试模式需要有效的输入文件、输出文件和答案文件')
            sys.exit(1)
        
        answers = []
        with open(args.answer, 'r', encoding='utf-8') as f:
            answers = f.readlines()
        if len(lines) != len(answers):
            print('测试模式需要有效的输入文件、输出文件和答案文件')
            sys.exit(1)
        
        word_num = 0
        correct_word_num = 0
        sentence_num = 0
        correct_sentence_num = 0

        for idx, line in enumerate(lines):
            pinyin = line.strip().split(' ')
            sentence = model.forward(pinyin)
            sentences.append(''.join(sentence))
            is_right = True
            word_num += len(sentence)
            for i in range(len(sentence)):
                if sentence[i] != answers[idx][i]:
                    is_right = False
                else:
                    correct_word_num += 1
            if is_right:
                correct_sentence_num += 1
            sentence_num += 1
        
        print('使用字元数为 %d 的字元模型' % args.ziyuan)
        print('测试句子数：%d, 包含 %d 字' % (sentence_num, word_num))
        print('正确句子数：%d, 正确 %d 字' % (correct_sentence_num, correct_word_num))
        print('句子正确率：%f' % (correct_sentence_num/sentence_num))
        print('字正确率：%f' % (correct_word_num/word_num))

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('使用字元数为 %d 的字元模型 \n' % args.ziyuan)
            f.write('测试句子数：%d, 包含 %d 字 \n' % (sentence_num, word_num))
            f.write('正确句子数：%d, 正确 %d 字 \n' % (correct_sentence_num, correct_word_num))
            f.write('句子正确率：%f \n' % (correct_sentence_num/sentence_num))
            f.write('字正确率：%f \n' % (correct_word_num/word_num))
    else:
        if len(lines)==0:
            pinyin = input('请输入一个句子的拼音，每个拼音间以空格分隔：')
            pinyin = pinyin.split(' ')
            sentence = model.forward(pinyin)
            print(''.join(sentence))
            sentences.append(''.join(sentence))
        else:
            for line in lines:
                pinyin = line.strip().split(' ')
                sentence = model.forward(pinyin)
                sentences.append(''.join(sentence))
                print(''.join(sentence))
    
    if args.output:
        with open(args.output, 'a', encoding='utf-8') as f:
            for sentence in sentences:
                f.write(sentence + '\n')