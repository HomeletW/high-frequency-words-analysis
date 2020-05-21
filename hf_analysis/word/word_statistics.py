"""
统计模块，用于总结重要高频词汇
"""
from __future__ import annotations

from statistics import mean, median
from typing import Any, Callable, Dict, FrozenSet, List, Tuple

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from hf_analysis.parameter import *

# the trend flags (趋势旗）

TREND_FLAG_STABLE = "stable"
"""
代表 稳定型高频词汇

定义：词汇的出现频率几乎保持不变
"""

TREND_FLAG_DECLINE = "decline"
"""
代表 衰退型高频词汇

定义：词汇的出现频率几乎一直在递减
"""

TREND_FLAG_INCREASE = "increase"
"""
代表 新生型高频词汇

定义：词汇的出现频率几乎一直在递增
"""


class StatisticalAnalyzer:
    """
    通过统计分析来总结此数据里的重要词汇

    ！必须实现 analyse 方法 !

    Note:此类为抽象类，不应直接引用

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    """
    # [ ({article_name: {word: count}}, category, order_index), ... ]
    _lst: List[Tuple[Dict[str, Dict[str, Tuple[int, float]]], str, int]]

    def __init__(self,
                 lst: List[Tuple[Dict[str, Dict[
                     str, Tuple[int, float]]], str, int]]) -> None:
        """初始化 StatisticalAnalyzer"""
        self._lst = lst

    def words(self) -> FrozenSet[str]:
        """返回所有的词汇"""
        return frozenset(
            word for articles, _, _ in self._lst for article in
            articles.values() for word in article
        )

    def values(self, words: FrozenSet[str] = None) -> \
            Dict[str, List[Tuple[int, Dict[str, Tuple[int, float]], str, int]]]:
        """返回所有词汇的对应年份的出现频率"""
        if words is None:
            words = self.words()
        return {word: [
            (
                sum(article.get(word, (0, None))[0] for article in
                    articles.values()),
                articles, category, order_index
            )
            for articles, category, order_index in self._lst
        ] for word in words}

    def frequency(self,
                  values: Dict[str, List[Tuple[
                      int, Dict[str, Dict[str, int]], str, int]]] = None) -> \
            Dict[str, int]:
        """返回一个字典，键为 _lst 的词汇，值为出现次数"""
        if values is None:
            values = self.values()
        return {
            word: sum(v for v, _, _, _ in years) for word, years in
            values.items()
        }

    def offsets(self,
                values: Dict[str, List[Tuple[
                    int, Dict[str, Tuple[int, float]], str, int]]] = None) -> \
            Dict[str, List[int]]:
        """返回所有单词的 offset 值"""
        if values is None:
            values = self.values()
        return {
            word: self._get_offset(years) for word, years in values.items()
        }

    @staticmethod
    def _get_offset(
            value: List[Tuple[int, Dict[str, Tuple[int, float]],
                              str, int]]) -> \
            List[int]:
        """返回 value 的 offset 值"""
        offsets = []

        last = None
        for this, _, _, _ in value:
            if last is not None:
                offsets.append(this - last)
            last = this
        return offsets

    @staticmethod
    def rank(scores: Dict[str, Any],
             key: Callable = lambda a: a) -> List[Tuple[str, Any]]:
        """
        返回一个排序过的列表，排序规则的 key 返回的值，与 List.sort 的 key 参数相同。

        Note:本方法为辅助方法

        参数列表如下：
        :param scores: 一个列表，键为词汇，值为词汇的衡量值，scores
        :param key: 排序 key 方法

        返回参数如下：
        :return: 一个由高到低排过序的列表
        """
        return sorted(
            ((word, value) for word, value in scores.items()),
            key=lambda a: key(a[1]), reverse=True
        )

    def analyse(self, *args, **kwargs) -> List[Tuple[str, Any]]:
        """
        返回一个排序过的列表，报告词汇分析结果

        返回参数如下：
        :return: -个字典报告重要高频词汇
        """
        raise NotImplementedError

    @classmethod
    def const(cls,
              lst: List[
                  Tuple[Dict[str, Dict[str, Tuple[int, float]]], str, int]]):
        """创建一个 StatisticalAnalyzer object"""
        return cls(lst)


class FrequencyAnalyzer(StatisticalAnalyzer):
    """
    使用 出现频率 作为衡量条件的分析器

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    """
    _lst: List[Tuple[Dict[str, Dict[str, int]], str, int]]

    def analyse(self, **kwargs) -> List[Tuple[str, Any]]:
        return self.rank(self.frequency())


class TrendAnalyzer(StatisticalAnalyzer):
    """
    使用 变化趋势 作为衡量条件的分析器

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    """
    _lst: List[Tuple[Dict[str, Dict[str, int]], str, int]]
    _threshold: Tuple[float, float]

    def __init__(self,
                 lst: List[Tuple[Dict[str, Dict[str, int]], str, int]]) -> None:
        super().__init__(lst)
        self._threshold = (-0.4, 0.4)

    def analyse(self, **kwargs) -> List[Tuple[str, Any]]:
        """
        返回一个集 包括 _num_wanted 个在 _lst 的重要高频词汇

        算法简介：
         根据 linear regression 的 coefficient 给以下词汇分类
            稳定型高频词汇:
                - TREND_FLAG_STABLE
                - 定义：词汇的出现频率几乎保持不变
            衰退型高频词汇
                - TREND_FLAG_DECLINE
                - 定义：词汇的出现频率几乎一直在递减
            新生型高频词汇
                - TREND_FLAG_INCREASE
                - 定义：词汇的出现频率几乎一直在递增
        """
        tracker = kwargs["tracker"]
        values = kwargs.get("values", self.values())
        trends_score = {}
        tracker.init_ticker("   进程", "正在分析", 0, len(values))
        for word, years in values.items():
            value = [y[0] for y in years]
            coef_ = None
            intercept_ = None
            RMSE = None
            label = None
            if len(value) >= 2:
                # we build the module
                x = np.array(range(len(value))).reshape(-1, 1)
                y = np.array(value).reshape(-1, 1)
                x_train, x_test, y_train, y_test = train_test_split(
                    x, y, test_size=0.2, random_state=0
                )
                reg = LinearRegression()
                reg.fit(x_train, y_train)
                y_pred = reg.predict(x_test)
                coef_ = reg.coef_
                intercept_ = reg.intercept_
                # calculate RMSE
                RMSE = np.sqrt(metrics.mean_squared_error(y_test, y_pred))
                label = self._label(intercept_, coef_)
            # calculate mean, median, max, min
            mean_ = mean(value)
            median_ = median(value)
            max_ = max(years, key=lambda a: a[0])
            min_ = min(years, key=lambda a: a[0])
            score_dict = {
                "coeff": coef_,  # the slop
                "inter": intercept_,  # the interception
                "RMSE": RMSE,  # how good this module is
                "label": label,  # the label of this word
                "mean": mean_,
                "median": median_,
                "max": max_,
                "min": min_,
                "value": value,
                "detail": [(detail, category, order_index) for
                           _, detail, category, order_index in years],
            }
            trends_score[word] = score_dict
            tracker.tick(disc_fill=" {}".format(word))
            tracker.tick_parent()
        return self.rank(
            trends_score, key=lambda a: (a["coeff"], a["max"])
        )

    def _label(self, intercept, coeff: np.array) -> str:
        """给此预测标签"""
        if coeff <= self._threshold[0]:
            return TREND_FLAG_DECLINE
        elif coeff >= self._threshold[1]:
            return TREND_FLAG_INCREASE
        else:
            return TREND_FLAG_STABLE


def analyze(segment, tracker, statistics_analyzer=TrendAnalyzer, **kwargs):
    """
    :param segment:
    :param tracker:
    :param statistics_analyzer: 用做分析器的统计分析器，应为 StatisticalAnalyzer 的子类
    """
    tracker.log("正在分析数据统计", prt=True)
    # create the statistical analyzer
    analyzer = ANALYZER[statistics_analyzer].const(segment)
    values = analyzer.values()
    tracker.init_parent_progress(
        "统计分析父程序", 0, len(values)
    )
    # analyze the data
    kwargs["tracker"] = tracker
    kwargs["values"] = values
    result = analyzer.analyse(**kwargs)
    return result


ANALYZER = {
    TREND_ANALYZER: TrendAnalyzer
}
