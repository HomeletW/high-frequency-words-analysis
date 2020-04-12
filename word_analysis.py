# coding=utf-8
import sys
from typing import Type

# 引用必要库
import jieba.analyse
import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt
import pandas as pd
import textract

from word_statistics import *

sys.path.append("./")

# 画图环境准备
font_path = "./SourceHanSerifSC-Light.otf"
prop = mfm.FontProperties(fname=font_path)
shapes = ["v", "s", "h", "o", "*", "p", "P", "H", "+", "x", "X", "d", "D"]

# 建议关键词路径
suggestion_path = "./suggestion_word.txt"

# 装载用户自定义字典
jieba.load_userdict(suggestion_path)

# 可用的提取器
TF_IDF = jieba.analyse.extract_tags
TEXT_RANK = jieba.analyse.textrank


def extract(sentence: str,
            suggestion_word: List[str],
            whitelist_word: List[str],
            num_wanted: int,
            extractor=TEXT_RANK) -> Dict[str, int]:
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
    :param suggestion_word: 想要一定被考虑的关键词列表
    :param whitelist_word: 想要一定出现的关键词列表
    :param num_wanted: 想要的关键词的个数 （抓取 10倍该值的关键词）
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)

    返回参数如下：
    :return: 返回一个字典，键为关键词，值为关键词出现在文章里出现的次数
    """
    # use jieba.analyse (tf-idf) or (TextRank)
    seg_list = extractor(
        sentence=sentence, topK=num_wanted * 10, withWeight=False, allowPOS=(
            "n",  # 普通名词
            "nr", "PER",  # 人名
            "nz",  # 专有名词
            "ns", "LOC",  # 地名
            "s",  # 处所名词
            "nt", "ORG",  # 机构名
            "nw",  # 作品名
        )
    )
    # use jieba.cut
    segments = jieba.lcut(sentence=sentence)
    # summaries
    summary = {seg: segments.count(seg) for seg in seg_list}
    # add suggestion word and whitelist word
    summary.update({word: segments.count(word) for word in suggestion_word if
                    word not in summary})
    summary.update({word: segments.count(word) for word in whitelist_word if
                    word not in summary})
    return summary


def read_file(path: str) -> str:
    """打开一个文件并读取其全部资源"""
    with open(path, "r", encoding="UTF-8") as f:
        return f.read()


def read_word_file(path: str) -> str:
    """打开一个 .doc .docx 文件并读取其全部资源"""
    return textract.process(path, encoding="UTF-8")


def load_suggestion_word(path: str) -> List[str]:
    """装载用户自定建议词典"""
    ls = read_file(path).split("\n")
    ls.remove("")
    return ls


def draw(input_files: List[Tuple[str, str]],
         suggestion_word: List[str],
         whitelist_word: List[str],
         blacklist_word: List[str],
         num_wanted: int,
         size: Tuple[int, int],
         extractor=TEXT_RANK,
         statistics_analyzer: Type[StatisticalAnalyzer] = FrequencyAnalyzer,
         *args, **kwargs) -> None:
    """
    展示一个图像来展示在数据中的高频词汇

    参数列表如下：
    :param input_files: 一个列表含有 <分析文件的路径> 与 <x轴的标签>
    :param suggestion_word: 想要一定被考虑的关键词列表
    :param whitelist_word: 想要一定出现的关键词列表
    :param blacklist_word: 想要一定不出现的关键词列表
    :param num_wanted: 想要的关键词的个数
    :param size: 生成的图像大小,生产100倍像素的图像（例如：（12，6）生成图像为 1200px * 600px)
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)
    :param statistics_analyzer: 用做分析器的统计分析器，应为 StatisticalAnalyzer 的子类
    """
    header = [i[1] for i in input_files]
    input_path = [i[0] for i in input_files]
    # create a list
    years = [
        extract(
            read_file(path), suggestion_word, whitelist_word, num_wanted,
            extractor
        ) for path in input_path
    ]
    # create the statistical analyzer
    analyzer = statistics_analyzer.const(
        years, whitelist_word, blacklist_word
    )
    # analyze the important data
    labeled_words = analyzer.analyse(*args, **kwargs)
    ranked_words = {word: data for word, data, item in labeled_words if
                    item["label"] == TREND_FLAG_STABLE}
    ranked_words.update({"x": header})
    # create data frame
    data = pd.DataFrame(ranked_words)
    # draw
    plt.figure(1, figsize=size, dpi=100)
    ax = plt.subplot(111)
    for word, s in zip(ranked_words, shapes * 10):
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
    # save the graph to the default location
    # show the graph
    plt.show()


def main():
    prefix_path = "/example"
    input_files = [
        (f".{prefix_path}/政府工作报告-2016-3-17.txt", "2016大"),
        (f".{prefix_path}/政府工作报告-2017-3-5.txt", "2017大"),
        (f".{prefix_path}/政府工作报告-2018-3-5.txt", "2018大"),
        (f".{prefix_path}/政府工作报告-2019-3-5.txt", "2019大"),
    ]
    draw(
        input_files=input_files,
        suggestion_word=load_suggestion_word(suggestion_path),
        whitelist_word=[],
        blacklist_word=[],
        num_wanted=7,
        size=(12, 6),
        extractor=TF_IDF,
        statistics_analyzer=TrendAnalyzer,
        # threshold=3,
    )


if __name__ == "__main__":
    main()
