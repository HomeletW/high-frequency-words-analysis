# coding=utf-8
import sys
from typing import Dict, List, Tuple, Union

import jieba.analyse
import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append("./")

# 画图环境准备
font_path = "./SourceHanSerifSC-Light.otf"
prop = mfm.FontProperties(fname=font_path)
shapes = ["v", "s", "h", "o", "*", "p", "P", "H", "+", "x", "X", "d", "D"]

# 装载用户自定义词典
# 测试：装载用户词典效果并不理想
user_dict = "./user_dict"
# jieba.analyse.set_idf_path(user_dict)

# 可用的分析器
TF_IDF = jieba.analyse.extract_tags
TEXT_RANK = jieba.analyse.textrank


def extract(sentence: str,
            suggestion_word: List[str],
            threshold: int,
            analyzer=TEXT_RANK) -> Dict[str, int]:
    """
    使用 jieba（中文分词）库，对文章进行关键词提取，使用 TextRank 或者 TF-IDF 算法。

    算法简介：
    ->  TF-IDF: 常用信息检索与数据挖掘算法
    ->  TextRank:
        论文：http://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf
        基本思想:
            -将待抽取关键词的文本进行分词

            -以固定窗口大小(默认为5，通过span属性调整)，词之间的共现关系，构建图
            -计算图中节点的PageRank，注意是无向带权图

    参数列表如下：
    :param sentence: 文章本身
    :param suggestion_word: 想要一定出现的关键词列表
    :param threshold: 想要的关键词的个数 （抓取 10倍该值的关键词）
    :param analyzer: 用做分析器的算法，应该为（TF_IDF 或者 TEXT_RANK)

    返回参数如下：
    :return: 返回一个字典，key为关键词，value关键词出现在文章里出现的次数
    """
    # use jieba.analyse (tf-idf) or (TextRank)
    seg_list = analyzer(
        sentence=sentence, topK=threshold * 10, withWeight=False, allowPOS=(
            "n",  # 普通名词
            "nr", "PER",  # 人名
            "nz",  # 专有名词
            "ns", "LOC",  # 地名
            "s",  # 处所名词
            "nt", "ORG",  # 机构名
            "nw",  # 作品名
        )
    )
    # summaries
    summary = {seg: sentence.count(seg) for seg in seg_list}
    summary.update({word: sentence.count(word) for word in suggestion_word if
                    word not in summary})
    return summary


def read_file(path: str) -> str:
    """
    打开一个文件并读取其全部资源
    """
    with open(path, "r", encoding="UTF-8") as f:
        return f.read()


def analyse(years: List[Dict[str, int]],
            suggestion_word: List[str],
            threshold: int) -> Dict[str, Union[List[int], List[str]]]:
    """
    Analyse the given list and conclude the most important portion of data
    """
    # construct a frequency count to find the highest frequency
    frequency_count = {}
    for year in years:
        for word, count in year.items():
            frequency_count[word] = frequency_count.get(word, 0) + count
    # find the average
    for word, count in frequency_count.items():
        frequency_count[word] = count / len(years)
    # find the top ones
    top = sorted(list(frequency_count.items()),
                 key=lambda a: a[1],
                 reverse=True)[:threshold - len(suggestion_word)]
    # get the word we want i.e the ones from suggestion_word or
    # the top frequency
    ret_words = suggestion_word + [word for word, _ in top]
    return {
        word: [year.get(word, 0) for year in years]
        for word in ret_words
    }


def draw(input_files: List[Tuple[str, str]],
         suggestion_word: List[str],
         threshold: int,
         size: Tuple[int, int],
         analyzer=TEXT_RANK) -> None:
    """
    展示一个图像来展示在数据中的高频词汇

    参数列表如下：
    :param input_files: 一个列表含有 <分析文件的路径> 与 <x轴的标签>
    :param suggestion_word: 想要一定出现的关键词列表
    :param threshold: 想要的关键词的个数
    :param size: 生成的图像大小
    :param analyzer: 用做分析器的算法，应该为（TF_IDF 或者 TEXT_RANK)
    """
    header = [i[1] for i in input_files]
    input_path = [i[0] for i in input_files]
    # create a list
    years = [
        extract(read_file(path), suggestion_word, threshold, analyzer)
        for path in input_path
    ]
    ranked_words = analyse(years, suggestion_word, threshold)
    ranked_words.update({"x": header})
    # create data frame
    data = pd.DataFrame(ranked_words)
    plt.figure(1, figsize=size, dpi=100)
    ax = plt.subplot(111)
    for word, s in zip(ranked_words, shapes):
        if word != "x":
            plt.plot("x",
                     word,
                     data=data,
                     marker=s,
                     markerfacecolor="gray",
                     markersize=8,
                     c="black",
                     linewidth=2)
    # change the label
    for label in ax.get_xticklabels():
        label.set_fontproperties(prop)
    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height])
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102),
               loc='lower left',
               ncol=len(ranked_words),
               mode="expand",
               borderaxespad=0.,
               prop=prop)
    plt.show()


def main():
    input_files = [
        ("./政府工作报告-2016-3-17.txt", "2016大"),
        ("./政府工作报告-2017-3-5.txt", "2017大"),
        ("./政府工作报告-2018-3-5.txt", "2018大"),
        ("./政府工作报告-2019-3-5.txt", "2019大"),
    ]
    draw(
        input_files=input_files,
        suggestion_word=[
            "政府"
        ],
        threshold=10,
        size=(12, 6),
        analyzer=TEXT_RANK
    )


if __name__ == "__main__":
    main()
