"""
统计模块，用于总结重要高频词汇
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Optional, Tuple

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

    ！必须实现 analyse 方法 !

    Note:此类为抽象类，不应直接引用

    成员变量如下：
    === 私有变量 ===
    _lst: 包含每个文件的高频词汇汇总
    """
    _tags: Dict[str, Dict[str, Dict[str, Tuple[int, float]]]]
    _articles: Dict[str, Dict[str, str]]
    _sorting: Dict[str, int]

    def __init__(self, tags, articles, sorting) -> None:
        """初始化 StatisticalAnalyzer"""
        self._tags = tags
        self._articles = articles
        self._sorting = sorting

    def all_tags(self) -> FrozenSet[str]:
        """返回所有的词汇"""
        return frozenset(
            tag
            for articles in self._tags.values()
            for article in articles.values()
            for tag in article
        )

    def analyse(self, *args, **kwargs) -> Tuple[Dict, Dict]:
        """
        返回一个排序过的列表，报告词汇分析结果

        返回参数如下：
        :return: -个字典报告重要高频词汇
        """
        raise NotImplementedError

    @classmethod
    def const(cls, tags, articles, sorting):
        """创建一个 StatisticalAnalyzer object"""
        return cls(tags, articles, sorting)


class TrendAnalyzer(StatisticalAnalyzer):
    """
    使用 变化趋势 作为衡量条件的分析器
    """
    _tags: Dict[str, Dict[str, Dict[str, float]]]
    _articles: Dict[str, Dict[str, str]]
    _sorting: Dict[str, int]

    def __init__(self, tags, articles, sorting) -> None:
        super().__init__(tags, articles, sorting)
        self._threshold = (-0.4, 0.4)

    def analyse(self, **kwargs) -> Tuple[Dict, Dict]:
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
        tags = self.all_tags()
        tracker.init_ticker("   进程", "正在进行趋势分析", 0,
                            len(tags) + len(self._articles))
        # detail summary
        detail_summary = {}
        for category, articles in self._articles.items():
            tracker.update_disc_fill("分析类别 {}".format(category))
            detail_summary[category] = {
                tag: {name: article.count(tag) for name, article in
                      articles.items()}
                for tag in tags
            }
            tracker.tick()
        # total summary
        total_summary = {}
        for tag in tags:
            tracker.update_disc_fill("分析词汇 {}".format(tag))
            values = list(occ for _, occ in sorted(
                {category: sum(tags_detail[tag].values())
                 for category, tags_detail in detail_summary.items()}.items(),
                key=lambda i: self._sorting[i[0]]
            ))
            lr = self.linear_regression(values)
            label = self.label(lr)
            total_summary[tag] = {
                "occurrence": values,
                "regression": lr,
                "label": label,
            }
            tracker.tick()
        return total_summary, detail_summary

    @staticmethod
    def linear_regression(values) -> Optional[Tuple[float, float, float]]:
        if len(values) < 2:
            return None
        # we build the module
        x = np.array(range(len(values))).reshape(-1, 1)
        y = np.array(values).reshape(-1, 1)
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=0
        )
        reg = LinearRegression()
        reg.fit(x_train, y_train)
        y_pred = reg.predict(x_test)
        coefficient = reg.coef_
        intercept = reg.intercept_
        # calculate RMSE
        RMSE = np.sqrt(metrics.mean_squared_error(y_test, y_pred))
        return coefficient, intercept, RMSE

    def label(self, lr) -> Optional[str]:
        """给此预测标签"""
        if lr is None:
            return None
        coefficient, intercept, RMSE = lr
        if coefficient <= self._threshold[0]:
            return TREND_FLAG_DECLINE
        elif coefficient >= self._threshold[1]:
            return TREND_FLAG_INCREASE
        else:
            return TREND_FLAG_STABLE


def analyze(segment,
            articles,
            sorting,
            tracker,
            statistics_analyzer=TrendAnalyzer, **kwargs):
    from hf_analysis.parameter import ANALYZER
    tracker.log("正在分析数据统计", prt=True)
    # create the statistical analyzer
    analyzer = ANALYZER[statistics_analyzer].const(
        tags=segment,
        articles=articles,
        sorting=sorting,
    )
    # analyze the data
    kwargs["tracker"] = tracker
    result = analyzer.analyse(**kwargs)
    return result
