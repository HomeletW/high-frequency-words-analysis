"""
统计模块，用于总结重要高频词汇
"""
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

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

    ！必须实现 _summarize 方法 !

    Note:此类为抽象类，不应直接引用

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    _whitelist_word: 返回列表里一定包含的词汇
    _blacklist_word: 返回列表里一定不包含的词汇
    _num_wanted: 需要的重要高频词汇的个数

    === 前提条件 ===
    - _lst 里面词汇数量 >= _num_wanted
    - _num_wanted >= len(_whitelist_word)
    - _whitelist_word 与 _blacklist_word 交集为空集
    """
    _lst: List[Tuple[Dict[str, int], str]]
    _whitelist_word: List[str]
    _blacklist_word: List[str]

    def __init__(self,
                 lst: List[Tuple[Dict[str, int], str]],
                 whitelist_word: List[str],
                 blacklist_word: List[str]) -> None:
        """初始化 StatisticalAnalyzer"""
        self._lst = lst
        self._whitelist_word = whitelist_word
        self._blacklist_word = blacklist_word

    def _words(self) -> FrozenSet[str]:
        """返回所有的词汇"""
        return frozenset(
            word for year in self._lst for word, _ in year[0].items()
        )

    def _values(self, words: FrozenSet[str] = None) -> \
            Dict[str, List[Tuple[int, str]]]:
        """
        返回所有词汇的对应年份的出现频率

        返回参数如下：
        :return: 一个字典，键为词汇，值为 所有年份出现频率
        """
        return {word: [(count.get(word, 0), name) for count, name in self._lst]
                for word in (words if words is not None else self._words())}

    def _frequency(self, values: Dict[str, List[Tuple[int, str]]] = None) -> \
            Dict[str, int]:
        """
        返回一个字典，键为 _lst 的词汇，值为出现次数

        Note:本方法为辅助方法

        返回参数如下：
        :return: 一个字典包含所有词汇
        """
        return {
            word: sum(v for v, _ in value) for word, value in
            (values if values is not None else self._values()).items()
        }

    def _offsets(self, values: Dict[str, List[Tuple[int, str]]] = None) -> \
            Dict[str, List[int]]:
        """
        返回所有单词的 offset 值

        返回参数如下:
        :return: 一个字典，键为词汇，值为 offset 值
        """
        return {
            word: self._get_offset(value) for word, value in
            (values if values is not None else self._values()).items()
        }

    @staticmethod
    def _get_offset(value: List[Tuple[int, str]]) -> List[int]:
        """
        返回 value 的 offset 值
        """
        offsets = []
        last = None
        for this, _ in value:
            if last is not None:
                offsets.append(this - last)
            last = this
        return offsets

    def _rank(self, scores: Dict[str, Any],
              values: Dict[str, List[Tuple[int, str]]] = None,
              key: Callable = lambda a: a) -> \
            List[Tuple[str, List[Tuple[int, str]], Any]]:
        """
        返回一个排序过的列表，排序规则的 key 返回的值，与 List.sort 的 key 参数相同。

        该列表为 _whitelist_word 的超集，与 _blacklist_word 的交集为空

        Note:本方法为辅助方法

        参数列表如下：
        :param scores: 一个列表，键为词汇，值为词汇的衡量值，scores 一定包含所有 _whitelist_word
        :param values: 所有词汇的每年出现频率，若不提供，则重新计算

        返回参数如下：
        :return: 一个由高到低排过序的列表
        """
        if values is None:
            values = self._values()
        # rank and filter the blacklist
        return sorted(
            ((word, values[word], score) for word, score in scores.items()
             if word not in self._blacklist_word),
            key=lambda a: key(a[2]), reverse=True
        )

    def analyse(self, *args, **kwargs) -> \
            List[Tuple[str, List[Tuple[str, int]], Any]]:
        """
        返回一个排序过的列表，报告词汇分析结果，该列表包括：
            [(词汇，词汇每年出现频率，衡量标准), ... ]

        返回参数如下：
        :return: -个字典报告重要高频词汇
        """
        raise NotImplementedError

    @classmethod
    def const(cls,
              lst: List[Tuple[Dict[str, int], str]],
              whitelist_word: List[str],
              blacklist_word: List[str]):
        """创建一个 StatisticalAnalyzer object"""
        return cls(lst, whitelist_word, blacklist_word)


class FrequencyAnalyzer(StatisticalAnalyzer):
    """
    使用 出现频率 作为衡量条件的分析器

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    _whitelist_word: 返回列表里一定包含的词汇
    _blacklist_word: 返回列表里一定不包含的词汇

    === 前提条件 ===
    - _whitelist_word 与 _blacklist_word 交集为空集
    """
    _lst: List[Tuple[Dict[str, int], str]]
    _whitelist_word: List[str]
    _blacklist_word: List[str]
    _num_wanted: Optional[int]

    def analyse(self, **kwargs) -> List[Tuple[str, List[Tuple[int, str]], Any]]:
        return self._rank(self._frequency())


class TrendAnalyzer(StatisticalAnalyzer):
    """
    使用 变化趋势 作为衡量条件的分析器

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    _whitelist_word: 返回列表里一定包含的词汇
    _blacklist_word: 返回列表里一定不包含的词汇

    === 前提条件 ===
    - _whitelist_word 与 _blacklist_word 交集为空集
    - _lst 长度至少为 2
    - 0 <= _tolerance <= 100
    """
    _lst: List[Tuple[Dict[str, int], str]]
    _whitelist_word: List[str]
    _blacklist_word: List[str]
    _threshold: Tuple[float, float]

    def __init__(self, lst: List[Tuple[Dict[str, int], str]],
                 whitelist_word: List[str],
                 blacklist_word: List[str]) -> None:
        super().__init__(lst, whitelist_word, blacklist_word)
        self._threshold = (-0.4, 0.4)

    def analyse(self, **kwargs) -> List[Tuple[str, List[Tuple[int, str]], Any]]:
        """
        返回一个集 包括 _num_wanted 个在 _lst 的重要高频词汇

        算法简介：
         根据 linear regression 的 coefficient 给以下词汇分类
            稳定型高频词汇:
                - TREND_FLAG_STABLE
                - 定义：词汇的出现频率几乎保持不变
                - -0.2 < coefficient < 0.2
            衰退型高频词汇
                - TREND_FLAG_DECLINE
                - 定义：词汇的出现频率几乎一直在递减
                - coefficient >= 0.2
            新生型高频词汇
                - TREND_FLAG_INCREASE
                - 定义：词汇的出现频率几乎一直在递增
                - coefficient <= -0.2
        """
        values = self._values()
        trends_score = {}
        for word, value in values.items():
            # we build the module
            x = np.array(range(len(value))).reshape(-1, 1)
            y = np.array(list(v for v, _ in value)).reshape(-1, 1)
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.2, random_state=0
            )
            reg = LinearRegression()
            reg.fit(x_train, y_train)
            if reg.coef_ == 0:
                continue
            y_pred = reg.predict(x_test)
            RMSE = np.sqrt(metrics.mean_squared_error(y_test, y_pred))
            label = self._label(reg.coef_)
            score_dict = {
                "coeff": reg.coef_,  # the slop
                "inter": reg.intercept_,  # the interception
                "RMSE": RMSE,  # how good this module is
                "label": label  # the label of this word
            }
            trends_score[word] = score_dict
        return self._rank(
            trends_score, values=values, key=lambda a: a["coeff"]
        )

    def _label(self, coeff: np.array) -> str:
        """给此斜率标签"""
        if coeff <= self._threshold[0]:
            return TREND_FLAG_DECLINE
        elif coeff >= self._threshold[1]:
            return TREND_FLAG_INCREASE
        else:
            return TREND_FLAG_STABLE
