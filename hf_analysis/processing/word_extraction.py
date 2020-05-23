# coding=utf-8

# 引用必要库
from typing import Dict, List

import jieba.analyse
import jieba.posseg

from hf_analysis.parameter import EXTRACTOR, TEXT_RANK


def extract(article_name: str,
            article: str,
            whitelist_word: List[str],
            blacklist_word: List[str],
            extractor,
            tracker,
            allowPOS,
            num_wanted: int = None) -> Dict[str, float]:
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
    :param article_name: 文章标题
    :param article: 文章本身
    :param whitelist_word: 想要一定出现的关键词列表
    :param blacklist_word: 想要一定不出现的关键词列表
    :param num_wanted: 想要的关键词的个数
    :param tracker: 追踪器
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)
    :param allowPOS: 词性

    返回参数如下：
    :return: 返回一个字典，键为关键词，值为关键词出现在文章里出现的次数
    """
    tracker.update_disc_fill("抽取 {}".format(article_name))
    if num_wanted is not None and num_wanted <= 0:
        num_wanted = None
    # use jieba.analyse (tf-idf) or (TextRank)
    tags = extractor.extract_tags(
        sentence=article, topK=num_wanted, withWeight=True,
        allowPOS=allowPOS
    )
    # add whitelist word
    tags += [(w, None) for w in whitelist_word if w not in tags]
    # remove blacklist word
    summary = {
        tag: weight
        for tag, weight in tags if tag not in blacklist_word
    }
    tracker.tick()
    return summary


def summarise(data: Dict[str, Dict[str, str]],
              suggestion_word: List[str],
              whitelist_word: List[str],
              blacklist_word: List[str],
              tracker,
              allowPOS,
              num_wanted: int,
              extractor) -> \
        Dict[str, Dict[str, Dict[str, float]]]:
    """
    总结所有的关键词汇

    参数列表如下：
    :param data: 数据
    :param suggestion_word: 建议关键词列表
    :param whitelist_word: 想要一定出现的关键词列表
    :param blacklist_word: 想要一定不出现的关键词列表
    :param tracker: 追踪器
    :param num_wanted: 想要的关键词的个数
    :param extractor: 用做提取器的算法，应该为（TF_IDF 或者 TEXT_RANK)
    :param allowPOS: 词性
    """
    # init the tracker
    # the total progress contains:
    #       each article in each year
    total_article_count = sum(
        1 for cat in data.values() for _ in cat
    )
    tracker.log("正在初始化 jieba 中文分词库", prt=True)
    jieba_instant = jieba.Tokenizer()
    # apply the suggestion word to jieba
    tracker.log("   正在装载 建议词汇 [word=[{},+{}个]]".format(
        ",".join(suggestion_word[:10]),
        0 if len(suggestion_word) < 10 else len(suggestion_word) - 10),
        prt=True)
    for word in suggestion_word:
        jieba_instant.add_word(word)
    # apply the whitelist word to jieba
    tracker.log("   正在装载 白名单词汇 [word=[{},+{}个]]".format(
        ",".join(whitelist_word[:10]),
        0 if len(whitelist_word) < 10 else len(whitelist_word) - 10),
        prt=True)
    for word in whitelist_word:
        jieba_instant.add_word(word)
    # apply the blacklist word to jieba
    tracker.log("   正在装载 黑名单词汇 [word=[{},+{}个]]".format(
        ",".join(blacklist_word[:10]),
        0 if len(blacklist_word) < 10 else len(blacklist_word) - 10),
        prt=True)
    for word in blacklist_word:
        jieba_instant.del_word(word)
    tracker.log("   正在抽取关键词汇", prt=True)
    tracker.init_ticker("    进程", "正在抽取词汇", 0, total_article_count)
    # extract the important word segment
    word_extractor = EXTRACTOR[extractor]()
    if extractor in [TEXT_RANK]:
        word_extractor.tokenizer = jieba.posseg.POSTokenizer(jieba_instant)
    else:
        word_extractor.tokenizer = jieba_instant
    tags = {
        category: {name: extract(
            name,
            article,
            whitelist_word,
            blacklist_word,
            word_extractor,
            tracker,
            allowPOS,
            num_wanted) for name, article in articles.items()}
        for category, articles in data.items()
    }
    return tags
