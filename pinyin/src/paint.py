import json
import math
from config import RESULT
import pyecharts.options as opts
from pyecharts.charts import Bar3D


def paint(x, x_name, y, y_name, data, z_name, title, min, max, file_name, width=80, depth=100):
    Bar3D(init_opts=opts.InitOpts(width="1000px", height="500px")).add(
        series_name="",
        data=[[d[0], d[1], d[2]] for d in data],
        xaxis3d_opts=opts.Axis3DOpts(
            data=x, type_="category", name=x_name),
        yaxis3d_opts=opts.Axis3DOpts(
            data=y, type_="category", name=y_name),
        zaxis3d_opts=opts.Axis3DOpts(
            type_="value", name=z_name, min_=min, max_=max),
        grid3d_opts=opts.Grid3DOpts(
            width=width, depth=depth),
    ).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            min_=min,
            max_=max,
            range_color=["#313695",
                         "#4575b4",
                         "#74add1",
                         "#abd9e9",
                         "#e0f3f8",
                         "#ffffbf",
                         "#fee090",
                         "#fdae61",
                         "#f46d43",
                         "#d73027",
                         "#a50026",],
        ),
        title_opts=opts.TitleOpts(title=title),

    ).render(f"html/{file_name}")


if __name__ == '__main__':
    data_sources = ['all', 'sina', 'baike', 'smp']

    alpha = [0.85, 0.90, 0.95, 0.99, 0.999, 0.9999, 0.99999]
    beta = [0.85, 0.90, 0.95, 0.99, 0.999, 0.9999, 0.99999]

    sent_corr = []
    word_corr = []
    min_sent = 1.0
    max_sent = 0.0
    min_word = 1.0
    max_word = 0.0

    for idx, source in enumerate(data_sources):
        with open(RESULT % source, 'r', encoding='utf-8') as f:
            results = json.load(f)
            for i, a in enumerate(alpha):
                sent_corr.append((idx, i, results['2'][str(a)][0]))
                word_corr.append((idx, i, results['2'][str(a)][1]))
                if results['2'][str(a)][0] < min_sent:
                    min_sent = results['2'][str(a)][0]
                if results['2'][str(a)][0] > max_sent:
                    max_sent = results['2'][str(a)][0]
                if results['2'][str(a)][1] < min_word:
                    min_word = results['2'][str(a)][1]
                if results['2'][str(a)][1] > max_word:
                    max_word = results['2'][str(a)][1]

    paint(data_sources, 'Data Source', alpha, 'Alpha', sent_corr, 'SentenceCorrectness',
          '二元模型下不同数据源不同 Alpha 的句子正确率', math.floor(min_sent*1000)/1000.0 - 0.001, math.floor(max_sent*1000)/1000.0 + 0.001, '2SentenceCorrection.html', width=80, depth=100)
    paint(data_sources, 'Data Source', alpha, 'Alpha', word_corr, 'WordCorrectness',
          '二元模型下不同数据源不同 Alpha 的字正确率', math.floor(min_word*1000)/1000.0 - 0.001, math.floor(max_word*1000)/1000.0 + 0.001, '2WordCorrection.html', width=80, depth=100)

    for idx, source in enumerate(data_sources):
        sent_corr = []
        word_corr = []
        min_sent = 1.0
        max_sent = 0.0
        min_word = 1.0
        max_word = 0.0
        with open(RESULT % source, 'r', encoding='utf-8') as f:
            results = json.load(f)
            for i, b in enumerate(beta):
                for j, a in enumerate(alpha):
                    sent_corr.append((i, j, results['3'][str(b)][str(a)][0]))
                    word_corr.append((i, j, results['3'][str(b)][str(a)][1]))
                    if results['3'][str(b)][str(a)][0] < min_sent:
                        min_sent = results['3'][str(b)][str(a)][0]
                    if results['3'][str(b)][str(a)][0] > max_sent:
                        max_sent = results['3'][str(b)][str(a)][0]
                    if results['3'][str(b)][str(a)][1] < min_word:
                        min_word = results['3'][str(b)][str(a)][1]
                    if results['3'][str(b)][str(a)][1] > max_word:
                        max_word = results['3'][str(b)][str(a)][1]
            paint(beta, 'Beta', alpha, 'Alpha', sent_corr, 'SentenceCorrectness',
                  f'训练{source}数据，三元模型下不同 Beta 不同 Alpha 的句子正确率', math.floor(min_sent*1000)/1000.0 - 0.001, math.floor(max_sent*1000)/1000.0 + 0.001, f'3SentenceCorrection_{source}.html', width=100, depth=100)
            paint(beta, 'Beta', alpha, 'Alpha', word_corr, 'WordCorrectness',
                  f'训练{source}数据，三元模型下不同 Beta 不同 Alpha 的字正确率', math.floor(min_word*1000)/1000.0 - 0.001, math.floor(max_word*1000)/1000.0 + 0.001, f'3WordCorrection_{source}.html', width=100, depth=100)
