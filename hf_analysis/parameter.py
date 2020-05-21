import platform
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

DEVICE_OS = platform.system()

DATA_PREFIX = "data"

# tesseract arguments
TESSDATA_PATH = ".././tessdata_best/."
FORMAT_LENGTH = 50

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

# available extractor
TREND_ANALYZER = "trend_analyzer"

# tracker constant
TRACKER_LOG = "tracker_log"
TRACKER_TICK = "tracker_tick"
TRACKER_PARENT_TICK = "tracker_parent_tick"
TRACKER_TICK_INIT = "tracker_tick_init"
TRACKER_PARENT_INIT = "tracker_parent_init"

TRACKER_LOG_DEBUG = DEBUG
TRACKER_LOG_INFO = INFO
TRACKER_LOG_WARNING = WARNING
TRACKER_LOG_ERROR = ERROR
TRACKER_LOG_CRITICAL = CRITICAL

# pdf engin
PDF_ENGINE_PDFTOCAIRO = True
PDF_ENGINE_PDFTOPPM = False

# info_handler entry
INFO_PATH_INDEX = "path_index"
INFO_PATH_ADDITIONAL_PARM = "path_additional_parm"
INFO_PATH_ROOT = "path_root"

INFO_PDF_DPI = "pdf_dpi"
INFO_PDF_FORMAT = "pdf_cov_format"
INFO_PDF_ENGINE = "pdf_engine"

INFO_OCR_DEF_LANG = "ocr_default_lang"

INFO_LOADER_RAW_DATA = "loader_raw_data"
INFO_EXTRACTOR_SEGMENTS = "extractor_segments"
INFO_ANALYZED_DATA = "analyzed_data"

INFO_ACTION_AUTO_NEXT_STEP = "action_auto_next_step"

INFO_ANALYZE_SUGGESTION_WORD = "analyze_suggestion"
INFO_ANALYZE_WHITELIST_WORD = "analyze_whitelist"
INFO_ANALYZE_BLACKLIST_WORD = "analyze_blacklist"
INFO_ANALYZE_NUM_WANTED = "analyze_num_wanted"
INFO_ANALYZE_EXTRACTOR = "analyze_extractor"
INFO_ANALYZE_STAT_ANALYZER = "analyze_stat_analyzer"

INFO_FIELD_NAME = {
    INFO_PATH_INDEX: "索引文件",
    INFO_PATH_ADDITIONAL_PARM: "附加参数文件",
    INFO_PATH_ROOT: "根目录",

    INFO_PDF_DPI: "PDF 扫描DPI",
    INFO_PDF_FORMAT: "PDF 扫描格式",
    INFO_PDF_ENGINE: "PDF 处理引擎",

    INFO_OCR_DEF_LANG: "OCR 默认语言",

    INFO_ANALYZE_SUGGESTION_WORD: "建议词汇",
    INFO_ANALYZE_WHITELIST_WORD: "白名单词汇",
    INFO_ANALYZE_BLACKLIST_WORD: "黑名单词汇",

    INFO_ANALYZE_NUM_WANTED: "抽取词汇数目",
    INFO_ANALYZE_EXTRACTOR: "高频词汇抽取器",

    INFO_ANALYZE_STAT_ANALYZER: "统计处理器",
}

THREAD_VALUE_ERROR = "value_error"
THREAD_OTHER_ERROR = "other_error"
