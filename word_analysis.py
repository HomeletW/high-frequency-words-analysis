# coding=utf-8
from os.path import join, exists
from os import makedirs
from typing import Type

# 引用必要库
import jieba.analyse
import matplotlib.font_manager as mfm
import matplotlib.pyplot as plt

from prepare_data import load_suggestion_word, prepare_data
from word_statistics import *

# 画图环境准备
font_path = "./resource/SourceHanSerifSC-Light.otf"
prop = mfm.FontProperties(fname=font_path)
shapes = ["v", "s", "h", "o", "*", "p", "P", "H", "+", "x", "X", "d", "D"]
COMMENT_OFFSET = 10

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
    :param num_wanted: 想要的关键词的个数
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)

    返回参数如下：
    :return: 返回一个字典，键为关键词，值为关键词出现在文章里出现的次数
    """
    # use jieba.analyse (tf-idf) or (TextRank)
    seg_list = extractor(
        sentence=sentence, topK=num_wanted, withWeight=False, allowPOS=(
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


def summarise(path: str,
              output_path: str,
              suggestion_word: List[str],
              whitelist_word: List[str],
              blacklist_word: List[str],
              num_wanted: int,
              size: Tuple[int, int],
              extractor=TEXT_RANK,
              statistics_analyzer: Type[StatisticalAnalyzer] = TrendAnalyzer,
              *args, **kwargs) -> None:
    """
    总结所有的关键词汇

    参数列表如下：
    :param path: 一个指向所有 data 文件的路径
    :param output_path: 一个指向所有结果参数的输出路径
    :param suggestion_word: 想要一定被考虑的关键词列表
    :param whitelist_word: 想要一定出现的关键词列表
    :param blacklist_word: 想要一定不出现的关键词列表
    :param num_wanted: 想要的关键词的个数
    :param size: 生成的图像大小,输出100倍像素的图像（例如：（12，6）生成图像为 1200px * 600px)
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)
    :param statistics_analyzer: 用做分析器的统计分析器，应为 StatisticalAnalyzer 的子类
    """
    # make sure output path is available
    if not exists(output_path):
        makedirs(output_path)
    # prepare the data
    data = prepare_data(path)
    # extract the important word segment in format [(dict of words, label), ...]
    seg = [
        (extract(
            content, suggestion_word, whitelist_word, num_wanted * 10, extractor
        ), name) for content, name in data
    ]
    # create the statistical analyzer
    analyzer = statistics_analyzer.const(seg, whitelist_word, blacklist_word)
    # analyze the data
    labeled_words = analyzer.analyse(*args, **kwargs)
    extrema = get_extrema(labeled_words)
    for value, rank in zip(labeled_words, range(len(labeled_words))):
        word, data, score = value
        draw_once(word, data, output_path, f"{rank}_{word}", size, extrema)


def get_extrema(data: List[Tuple[str, List[Tuple[int, str]], Any]]) -> \
        Tuple[int, int]:
    max_, min_ = None, None
    for _, value, _ in data:
        max_v, min_v = max(value, key=lambda a: a[0])[0], \
                       min(value, key=lambda a: a[0])[0]
        if max_ is None or max_v > max_:
            max_ = max_v
        if min_ is None or min_v < min_:
            min_ = min_v
    return min_, max_


def draw_once(word: str,
              data: List[Tuple[int, str]],
              path: str,
              file_name: str,
              size: Tuple[int, int],
              extrema: Tuple[int, int]) -> None:
    """
    展示一个图像来展示在数据中的高频词汇
    """
    fig = prepare_graph(word, size, 1, extrema)
    # draw the graph
    plt.plot(list(name for _, name in data), list(v for v, _ in data),
             marker="v",
             markerfacecolor="gray",
             markersize=8,
             c="black",
             linewidth=2)
    # draw the comment
    for index, value in zip(range(len(data)), data):
        plt.text(index, value[0] + COMMENT_OFFSET,
                 s=str(value[0]), fontproperties=prop)
    # save and exit
    plt.savefig(join(path, file_name))
    plt.close(fig)


def prepare_graph(name: str,
                  size: Tuple[int, int],
                  ncol: int,
                  extrema: Tuple[int, int]) -> plt.Figure:
    fig = plt.figure(name, figsize=size, dpi=100)
    ax = plt.axes()
    for label in ax.get_xticklabels():
        label.set_fontproperties(prop)
    # Shrink current axis's height by 10% on the bottom
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width, box.height])
    # ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
    #           ncol=ncol, mode="expand", borderaxespad=0., prop=prop)
    min_, max_ = extrema
    ax.set_title(f"“{name}”的总结", fontproperties=prop)
    ax.set_ylabel(f"“{name}”每年的数量", fontproperties=prop)
    ax.set_ylim(min_, max_)
    return fig


def main():
    summarise(
        path="./data/output",
        output_path="./data/result",
        suggestion_word=[],
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
