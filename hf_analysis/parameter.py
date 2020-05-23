import platform
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

import jieba.analyse

from processing.word_statistics import TREND_FLAG_DECLINE, \
    TREND_FLAG_INCREASE, TREND_FLAG_STABLE, TrendAnalyzer

DEVICE_OS = platform.system()

ADDI_PARM_CROP = "CROP"
ADDI_PARM_LANG = "LANG"

DATA_PREFIX = "data"

TREND_NAME = {
    TREND_FLAG_STABLE: "稳定型",
    TREND_FLAG_DECLINE: "衰退型",
    TREND_FLAG_INCREASE: "新生型",
}

# tesseract arguments
TESSDATA_DEFAULT_PATH = ".././tessdata/default/."
TESSDATA_BEST_PATH = ".././tessdata/best/."
TESSDATA_FAST_PATH = ".././tessdata/fast/."
FORMAT_LENGTH = 50

DEFAULT_SPACING = 5

# default path parameter
TEMP_PATH = "temp"
DATA_PATH = "data"
RESOURCE_PATH = "resource"

# log path
LOG_PATH = ".././log/"

# json path
JSON_PATH = "./.././default.json"

# available extractor
TF_IDF = "tf-idf"
TEXT_RANK = "TextRank"

# 可用的提取器
EXTRACTOR = {
    TF_IDF: jieba.analyse.TFIDF,
    TEXT_RANK: jieba.analyse.TextRank,
}

# available extractor
TREND_ANALYZER = "trend_analyzer"

ANALYZER = {
    TREND_ANALYZER: TrendAnalyzer
}

# tracker constant
TRACKER_LOG = "tracker_log"
TRACKER_TICK = "tracker_tick"
TRACKER_TICK_DESC_UPDATE = "tracker_tick_description_update"
TRACKER_TICK_INIT = "tracker_tick_init"
TRACKER_SET_INDETERMINATE = "tracker_indeterminate"

TRACKER_LOG_DEBUG = DEBUG
TRACKER_LOG_INFO = INFO
TRACKER_LOG_WARNING = WARNING
TRACKER_LOG_ERROR = ERROR
TRACKER_LOG_CRITICAL = CRITICAL

# pdf engin
PDF_ENGINE_PDFTOCAIRO = True
PDF_ENGINE_PDFTOPPM = False

INFO_PATCH = "patch"
# info_handler entry
INFO_PATH_INDEX = "path_index"
INFO_PATH_ADDITIONAL_PARM = "path_additional_parm"
INFO_PATH_ROOT = "path_root"

INFO_PDF_DPI = "pdf_dpi"
INFO_PDF_FORMAT = "pdf_cov_format"
INFO_PDF_ENGINE = "pdf_engine"

INFO_OCR_DEF_LANG = "ocr_default_lang"
INFO_OCR_TESSDATA_PATH = "ocr_tessdata_path"

INFO_INDEX_MAP = "index_map"
INFO_ARTICLES = "articles"
INFO_SORTING = "sorting"
INFO_TAGS = "tags"
INFO_ANALYZED_SUMMARY = "analyzed_summary"
INFO_ANALYZED_DETAIL = "analyzed_detail"

INFO_ACTION_AUTO_NEXT_STEP = "action_auto_next_step"
INFO_ACTION_SHOW_STAT_DETAIL = "analyze_show_stat_detail"

INFO_ANALYZE_ALLOW_POS = "analyze_ALLOW"
INFO_ANALYZE_SUGGESTION_WORD = "analyze_suggestion"
INFO_ANALYZE_WHITELIST_WORD = "analyze_whitelist"
INFO_ANALYZE_BLACKLIST_WORD = "analyze_blacklist"
INFO_ANALYZE_NUM_WANTED = "analyze_num_wanted"
INFO_ANALYZE_EXTRACTOR = "analyze_extractor"
INFO_ANALYZE_STAT_ANALYZER = "analyze_stat_analyzer"

INFO_OUTPUT_PATH = "output_path"

POS_OPTIONS = {
    "n": "普通名词",
    "nr": "人名",
    "nz": "其他专名",
    "a": "形容词",
    "m": "数量词",
    "c": "连词",
    "PER": "人名(专名)",
    "f": "方位名词",
    "ns": "地名",
    "v": "普通动词",
    "ad": "副形词",
    "q": "量词",
    "u": "助词",
    "LOC": "地名(专名)",
    "s": "处所名词",
    "nt": "机构名",
    "vd": "动副词",
    "an": "名形词",
    "r": "代词",
    "xc": "其他虚词",
    "ORG": "机构名(专名)",
    "t": "时间",
    "nw": "作品名",
    "vn": "名动词",
    "d": "副词",
    "p": "介词",
    "w": "标点符号",
    "TIME": "时间(专名)",
}

DEFAULT_POS = [
    "n",  # 普通名词
    "nr", "PER",  # 人名
    "nz",  # 专有名词
    "ns", "LOC",  # 地名
    "s",  # 处所名词
    "nt", "ORG",  # 机构名
    "nw",  # 作品名
]

INFO_FIELD_NAME = {
    INFO_PATH_INDEX: "索引文件",
    INFO_PATH_ADDITIONAL_PARM: "附加参数文件",
    INFO_PATH_ROOT: "根目录",

    INFO_PDF_DPI: "PDF 扫描DPI",
    INFO_PDF_FORMAT: "PDF 扫描格式",
    INFO_PDF_ENGINE: "PDF 处理引擎",

    INFO_OCR_DEF_LANG: "OCR 默认语言",
    INFO_OCR_TESSDATA_PATH: "OCR 优先级",

    INFO_ANALYZE_ALLOW_POS: "词性筛选",
    INFO_ANALYZE_SUGGESTION_WORD: "建议词汇",
    INFO_ANALYZE_WHITELIST_WORD: "白名单词汇",
    INFO_ANALYZE_BLACKLIST_WORD: "黑名单词汇",

    INFO_ANALYZE_NUM_WANTED: "抽取词汇数目",
    INFO_ANALYZE_EXTRACTOR: "高频词汇抽取器",

    INFO_ANALYZE_STAT_ANALYZER: "统计处理器",
    INFO_ACTION_SHOW_STAT_DETAIL: "输出统计细节",

    INFO_OUTPUT_PATH: "输出目录",
}

THREAD_VALUE_ERROR = "value_error"
THREAD_OTHER_ERROR = "other_error"
