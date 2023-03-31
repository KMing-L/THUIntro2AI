import argparse
import json
from model import WordModel

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_from', type=str, help='sina, smp, all, baike')
    parser.add_argument('--part', type=int, default=0)
    args = parser.parse_args()
    
    ZiYuan = [2, 3]
    Alpha = [0.5, 0.6, 0.7, 0.8, 0.85, 0.90, 0.95, 0.999]
    Beta = [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.999]
    if args.part == 1:
        Beta = [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
    elif args.part == 2:
        Beta = [0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.999]

    with open('test/input.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open('test/std_output.txt', 'r', encoding='utf-8') as f:
        answers = f.readlines()

    results_txt = []
    results_json = {}

    for ziyuan in ZiYuan:
        results_json[ziyuan] = {}
        model = WordModel(ziyuan=ziyuan, data_from=args.data_from)
        for beta in Beta:
            if ziyuan == 3:
                results_json[ziyuan][beta] = {}
            for alpha in Alpha:
                model.set(alpha, beta)
                word_num = 0
                correct_word_num = 0
                sentence_num = 0
                correct_sentence_num = 0

                print(f'test {args.data_from} {ziyuan} {alpha} {beta}')

                for idx in range(len(lines)):
                    line = lines[idx]
                    pinyin = line.strip().split(' ')
                    sentence = model.forward(pinyin)
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
                if ziyuan == 2:
                    results_txt.append(
                        f'{args.data_from} {ziyuan} alpha={alpha} sentence_acc={correct_sentence_num/sentence_num} word_acc={correct_word_num/word_num}')
                    results_json[ziyuan][alpha] = (correct_sentence_num/sentence_num, correct_word_num/word_num)
                else:
                    results_txt.append(
                        f'{args.data_from} {ziyuan} alpha={alpha} beta={beta} sentence_acc={correct_sentence_num/sentence_num} word_acc={correct_word_num/word_num}')
                    results_json[ziyuan][beta][alpha] = (correct_sentence_num/sentence_num, correct_word_num/word_num)
            if ziyuan == 2:
                break
    
    file_name = f'out/test_result_{args.data_from}'
    if args.part != 0:
        file_name += f'_{args.part}'

    with open(file_name+'txt', 'w', encoding='utf-8') as f:
        for line in results_txt:
            f.write(line+'\n')
    with open(file_name+'json', 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=4)
