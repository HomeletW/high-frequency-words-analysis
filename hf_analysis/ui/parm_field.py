# -*- coding: utf-8 -*-

import subprocess
import tkinter.messagebox as messagebox
from tkinter.ttk import Progressbar

from pinyin import pinyin

from hf_analysis.ui.tk_object import *


class BaseFrame(tk.Frame, Sizeable):
    def __init__(self, master, size_conf, info_handler):
        width, height = size_conf.total_size()
        super().__init__(master, width=width, height=height)
        self.size_conf = size_conf
        self._info_handler = info_handler

    def add_items(self, *args, **kwargs):
        raise NotImplementedError

    def place_items(self):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()

    def set(self, entry, value):
        self._info_handler[entry] = value

    def get(self, entry, default=None):
        return self._info_handler.get(entry, default)


class LabeledBaseFrame(tk.LabelFrame, Sizeable):
    def __init__(self, master, text, size_conf, info_handler):
        width, height = size_conf.total_size()
        super().__init__(master, text=text, width=width, height=height)
        self.size_conf = size_conf
        self._info_handler = info_handler

    def add_items(self, *args, **kwargs):
        raise NotImplementedError

    def place_items(self):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()

    def set(self, entry, value):
        self._info_handler[entry] = value

    def get(self, entry, default=None):
        return self._info_handler.get(entry, default)


class LeftFileSelectFrame(LabeledBaseFrame):
    """
    [ ButtonLabelPair ] 1
    [ ButtonLabelPair ] 1
    [ ButtonLabelPair ] 1
    # [ ButtonLabelPair ] 1
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "文件选择", size_conf, info_handler)
        self.butt_root_directory = None
        self.butt_index_file = None
        self.butt_add_pram_file = None
        # self.butt_suggestion_file = None
        self.add_items()
        self.place_items()
        # register field
        self._info_handler.register_field(
            source=self.butt_root_directory,
            key=INFO_PATH_ROOT,
            default="",
            not_none=True,
            not_empty=True,
            type_=str
        )
        self._info_handler.register_field(
            source=self.butt_index_file,
            key=INFO_PATH_INDEX,
            default="",
            not_none=True,
            type_=str
        )
        self._info_handler.register_field(
            source=self.butt_add_pram_file,
            key=INFO_PATH_ADDITIONAL_PARM,
            not_none=True,
            default="",
            type_=str
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
            (1, 1),
            # (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.butt_root_directory = ButtonLabelPair(
            master=self, button_text="选择 根目录",
            button_func=self.open_root_directory, size_conf=divided[0][0],
            mandatory_field=True
        )
        self.butt_index_file = ButtonLabelPair(
            master=self, button_text="选择 索引文件",
            button_func=self.open_index_file, size_conf=divided[1][0],
            mandatory_field=True
        )
        self.butt_add_pram_file = ButtonLabelPair(
            master=self, button_text="选择 附加参数文件",
            button_func=self.open_additional_parm_file, size_conf=divided[2][0],
            mandatory_field=False
        )

    def place_items(self):
        self.size_conf.place((
            [self.butt_root_directory],
            [self.butt_index_file],
            [self.butt_add_pram_file],
            # [self.butt_suggestion_file],
        ))

    def open_index_file(self):
        cur_index_file = self.butt_index_file.get()
        if cur_index_file is not None and cur_index_file != "" and \
                cur_index_file != "-":
            initdir, _ = split(cur_index_file)
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_file(self, "选择 索引文件", (FILE_TYPE_EXCEL,),
                                initdir=initdir)
        if not ret_dir:
            return
        self.butt_index_file.set(ret_dir)

    def open_additional_parm_file(self):
        cur_add_parm = self.butt_add_pram_file.get()
        if cur_add_parm is not None and cur_add_parm != "" and \
                cur_add_parm != "-":
            initdir, _ = split(cur_add_parm)
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_file(self, "选择 附加参数文件",
                                (FILE_TYPE_EXCEL,), initdir=initdir)
        if not ret_dir:
            return
        self.butt_add_pram_file.set(ret_dir)

    def open_root_directory(self):
        cur_root_dir = self.butt_root_directory.get()
        if cur_root_dir is not None and cur_root_dir != "" and \
                cur_root_dir != "-":
            initdir = cur_root_dir
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_directory(self, "选择 根目录", initdir=initdir)
        if not ret_dir:
            return
        self.butt_root_directory.set(ret_dir)


class LeftPdfFrame(LabeledBaseFrame):
    """
    [ RadioButtonPair ]
    [ RadioButtonPair ]
    [ RadioButtonPair ]
    ======
    PDF Field:
        Engine                  pdftoppm / pdftocairo   ChoicePair
        PDF Scan Format         jpeg / tiff / png       ChoicePair
        DPI Field               300 ~ 600               ChoicePair
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "PDF 处理", size_conf, info_handler)
        self.select_pdf_engine = None
        self.select_pdf_scan_format = None
        self.select_pdf_dpi = None
        self.add_items()
        self.place_items()
        # register field
        self._info_handler.register_field(
            self.select_pdf_engine, key=INFO_PDF_ENGINE,
            default=PDF_ENGINE_PDFTOPPM,
            not_none=True,
            type_=bool
        )
        self._info_handler.register_field(
            self.select_pdf_scan_format, key=INFO_PDF_FORMAT,
            default="jpg",
            not_none=True,
            not_empty=True,
            type_=str
        )
        self._info_handler.register_field(
            self.select_pdf_dpi, key=INFO_PDF_DPI,
            default=300,
            not_none=True,
            type_=int
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
            (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.select_pdf_engine = RadioButtonsPair(
            master=self, label_text="选择 PDF 处理引擎", options=[
                ("pdftoppm", PDF_ENGINE_PDFTOPPM),
                ("pdftocairo", PDF_ENGINE_PDFTOCAIRO)
            ],
            var=tk.BooleanVar,
            size_conf=divided[0][0]
        )
        self.select_pdf_scan_format = RadioButtonsPair(
            master=self, label_text="选择 PDF 扫描格式", options=[
                ("jpg (推荐)", "jpg"),
                ("png", "png"),
                ("tiff", "tiff"),
            ],
            var=tk.StringVar,
            size_conf=divided[1][0]
        )
        self.select_pdf_dpi = RadioButtonsPair(
            master=self, label_text="选择 PDF 扫描DPI (速度快 - 效果清晰)", options=[
                ("300", 300),
                ("400", 400),
                ("500", 500),
                ("600", 600),
            ],
            var=tk.IntVar,
            size_conf=divided[2][0]
        )

    def place_items(self):
        self.size_conf.place((
            [self.select_pdf_engine],
            [self.select_pdf_scan_format],
            [self.select_pdf_dpi]
        ))


class LeftOCROpFrame(LabeledBaseFrame):
    """
    [ RadioButtonPair ]
    [ CheckButtonPair ]
    ======
    OCR Optimization Field:
        OCR 识别数据库            Text Input              RadioButtonPair
        Default language        Text Input              CheckButtonPair
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "OCR 优化", size_conf, info_handler)
        self.select_TESSDATA_PATH = None
        self.select_default_lang = None
        self.add_items()
        self.place_items()
        # register field
        self._info_handler.register_field(
            self.select_TESSDATA_PATH, key=INFO_OCR_TESSDATA_PATH,
            default=TESSDATA_DEFAULT_PATH,
            not_none=True,
            not_empty=True,
            type_=str
        )
        self._info_handler.register_field(
            self.select_default_lang, key=INFO_OCR_DEF_LANG,
            default="chi_sim",
            not_none=True,
            not_empty=True,
            type_=str
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
        ), spacing=0, internal=True, height_offset=21, width_offset=4)
        self.select_TESSDATA_PATH = RadioButtonsPair(
            master=self, label_text="选择 OCR 优先级", options=(
                ("优先速度", TESSDATA_FAST_PATH),
                ("平均", TESSDATA_DEFAULT_PATH),
                ("优先质量", TESSDATA_BEST_PATH),
            ), var=tk.StringVar, size_conf=divided[0][0]
        )
        self.select_default_lang = CheckButtonsPair(
            master=self, label_text="选择 OCR 默认语言", options=(
                ("简体中文", "chi_sim"),
                ("繁体中文", "chi_tra"),
            ), size_conf=divided[1][0]
        )

    def place_items(self):
        self.size_conf.place([
            [self.select_TESSDATA_PATH],
            [self.select_default_lang],
        ])

    def show_available_lang(self):
        # max_length = max(len(lang) for lang in AVAILABLE_LANG) + 3
        # avi_lang = "\n".join(
        #     "".join(
        #         lang.ljust(10, " ") for lang in AVAILABLE_LANG[i:i + 6]
        #     ) for i in range(0, len(AVAILABLE_LANG), 6)
        # )
        message = "选择语言时应遵守以下规则以增加识别准确度\n" \
                  "1. 尽量准确选择可能出现的语言\n" \
                  "2. 尽量排除不会出现的语言来减少干扰\n" \
                  "\n" \
                  "语言输入格式：\n" \
                  "    语言1+语言2+...\n" \
                  "\n" \
                  "例如：简体中文+英文 应为：chi_sim+eng\n" \
                  "\n" \
                  "关于 Tesseract-ocr 支持语言请前往：\n" \
                  "https://github.com/tesseract-ocr/tessdoc"
        tk.messagebox.showinfo(parent=self, title="语言选择与使用注意事项",
                               message=message)


class CentralInstructionFrame(BaseFrame):
    """
    [ label ]
    [ label ]
    """

    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.top_label = None
        self.bot_label = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 1),
            (4, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.top_label = tk.Label(master=self, text="image here")
        self.bot_label = tk.Label(master=self, text="instruction here")

    def place_items(self):
        self.size_conf.place([
            [self.top_label],
            [self.bot_label],
        ])


class CentralProgressBarFrame(BaseFrame):
    """
    [ label ]
    [ progressbar ]
    """

    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.label_var = None
        self.progress_current_var = None
        self.progress_label = None
        self.progress_bar_current = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        self.size_conf.divide((
            (2, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.label_var = tk.StringVar()
        self.label_var.set("欢迎！")
        self.progress_current_var = tk.IntVar()
        self.progress_label = tk.Label(master=self, textvariable=self.label_var,
                                       anchor=tk.CENTER)
        self.progress_bar_current = Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            mode="determinate",
            variable=self.progress_current_var
        )

    def place_items(self):
        self.size_conf.place([
            [self.progress_label],
            [self.progress_bar_current],
        ])

    def progress_update(self, **kwargs):
        mode = kwargs["mode"]
        if mode == TRACKER_TICK_INIT:
            process_disc = kwargs["process_disc"]
            total_tick = kwargs["total_tick"]
            init_tick = kwargs["init_tick"]
            self.label_var.set(process_disc)
            self.progress_bar_current["maximum"] = total_tick
            self.progress_current_var.set(init_tick)
            self.label_var.set(
                process_disc + " ({}/{})".format(init_tick, total_tick))
        elif mode == TRACKER_TICK:
            process_disc = kwargs["process_disc"]
            total_tick = kwargs["total_tick"]
            current_tick = kwargs["current_tick"]
            end = kwargs["end"]
            disc_fill = kwargs["disc_fill"]
            time_remain = kwargs["time_remain"]
            self.progress_current_var.set(current_tick)
            if end:
                self.progress_bar_current.stop()
                self.progress_bar_current.config(
                    mode="determinate"
                )
                self.label_var.set("结束!")
            else:
                message = "{} :{}{} 预计剩余: {}".format(
                    process_disc,
                    " " + (disc_fill if disc_fill is not None else ""),
                    " ({}/{})".format(current_tick, total_tick),
                    time_remain
                )
                self.label_var.set(message)
        elif mode == TRACKER_TICK_DESC_UPDATE:
            process_disc = kwargs["process_disc"]
            disc_fill = kwargs["process_disc_fill"]
            time_remain = kwargs["time_remain"]
            total_tick = kwargs["total_tick"]
            current_tick = kwargs["current_tick"]
            message = "{} :{}{} 预计剩余: {}".format(
                process_disc,
                " " + (disc_fill if disc_fill is not None else ""),
                " ({}/{})".format(current_tick, total_tick),
                time_remain
            )
            self.label_var.set(message)
        elif mode == TRACKER_SET_INDETERMINATE:
            indeterminate = kwargs["indeterminate"]
            process_disc = kwargs["process_disc"]
            disc_fill = kwargs["process_disc_fill"]
            if indeterminate:
                self.progress_bar_current.config(
                    mode="indeterminate"
                )
                self.progress_bar_current.start()
                message = "{} :{}".format(
                    process_disc,
                    " " + (disc_fill if disc_fill is not None else ""),
                )
                self.label_var.set(message)
            else:
                self.progress_bar_current.stop()
                self.progress_bar_current.config(
                    mode="determinate"
                )


class CentralActionFrame(BaseFrame):
    """
    [ button, button, button ]
    """

    def __init__(self, master, size_config, tracker, info_handler):
        super().__init__(master, size_config, info_handler)
        self.auto_next_step = None
        self.show_stat_detail = None
        self.preprocess_button = None
        self.review_preprocess_button = None
        self.load_data_button = None
        self.extraction_button = None
        self.review_extraction_button = None
        self.analyze_button = None
        self.export_button = None
        self._buttons = None
        self.export_path = DEFAULT_DIR
        self.tracker = tracker
        # threading
        self._preprocess_thread = ThreadWrapper(
            name="预处理",
            master=self.master,
            tracker=self.tracker,
            thread_type=PreprocessThread,
            info_handler=self._info_handler,
            start_process=self._starting_preprocess,
            end_process=self._ending_preprocess
        )
        self._load_data_thread = ThreadWrapper(
            name="装载数据",
            master=self.master,
            tracker=self.tracker,
            thread_type=LoadDataThread,
            info_handler=self._info_handler,
            start_process=self._starting_load_data,
            end_process=self._ending_load_data
        )
        self._extraction_thread = ThreadWrapper(
            name="抽取词汇",
            master=self.master,
            tracker=self.tracker,
            thread_type=ExtractionThread,
            info_handler=self._info_handler,
            start_process=self._starting_extraction,
            end_process=self._ending_extraction
        )
        self._analyze_thread = ThreadWrapper(
            name="统计分析",
            master=self.master,
            tracker=self.tracker,
            thread_type=AnalyzeThread,
            info_handler=self._info_handler,
            start_process=self._starting_analyze,
            end_process=self._ending_analyze
        )
        self._export_thread = ThreadWrapper(
            name="输出",
            master=self.master,
            tracker=self.tracker,
            thread_type=ExportThread,
            info_handler=self._info_handler,
            start_process=self._starting_export,
            end_process=self._ending_export
        )
        # start
        self.add_items()
        self.place_items()
        self.ordered = [
            INFO_ARTICLES,
            INFO_TAGS,
            INFO_ANALYZED_SUMMARY,
        ]
        self._info_handler.register_field(
            source=self.auto_next_step,
            default=True,
            key=INFO_ACTION_AUTO_NEXT_STEP,
            type_=bool
        )
        self._info_handler.register_field(
            source=self.show_stat_detail,
            default=True,
            key=INFO_ACTION_SHOW_STAT_DETAIL,
            type_=bool
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            key=INFO_ARTICLES,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            key=INFO_SORTING,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            key=INFO_TAGS,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            key=INFO_ANALYZED_SUMMARY,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            key=INFO_ANALYZED_DETAIL,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            key=INFO_OUTPUT_PATH,
        )
        self._sync_button()

    def add_items(self, *args, **kwargs):
        divide = self.size_conf.divide((
            (1, 2, 2, 1, 1),
            (2, 3, 3, 3, 3, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.auto_next_step = CheckButtonPair(
            master=self, text="自动开始下一步骤", size_conf=divide[0][0], anchor=tk.W
        )
        self.show_stat_detail = CheckButtonPair(
            master=self, text="输出统计细节", size_conf=divide[0][1], anchor=tk.W
        )
        self.preprocess_button = TwoStageButton(
            master=self, command=self._preprocess_thread.run,
            text_choice={True: "预处理", False: "预处理中..."},
            init_pos=True
        )
        self.review_preprocess_button = tk.Button(
            master=self, command=self.review_preprocess,
            text="校对预处理"
        )
        self.load_data_button = TwoStageButton(
            master=self, command=self._load_data_thread.run,
            text_choice={True: "装载数据", False: "数据装载中..."},
            init_pos=True
        )
        self.extraction_button = TwoStageButton(
            master=self, command=self._extraction_thread.run,
            text_choice={True: "抽取词汇", False: "词汇抽取中..."},
            init_pos=True
        )
        self.review_extraction_button = tk.Button(
            master=self, command=self.review_extraction,
            text="初步检查词汇"
        )
        self.analyze_button = TwoStageButton(
            master=self, command=self._analyze_thread.run,
            text_choice={True: "统计分析", False: "统计分析中..."},
            init_pos=True
        )
        self.export_button = tk.Button(
            master=self, command=self._export_thread.run,
            text="输出", fg="red"
        )
        self._buttons = [
            self.auto_next_step,
            self.show_stat_detail,
            self.preprocess_button,
            self.review_preprocess_button,
            self.load_data_button,
            self.extraction_button,
            self.review_extraction_button,
            self.analyze_button,
            self.export_button
        ]

    def place_items(self):
        self.size_conf.place([
            [self.auto_next_step,
             self.show_stat_detail,
             self.review_preprocess_button,
             self.review_extraction_button],
            [self.preprocess_button,
             self.load_data_button,
             self.extraction_button,
             self.analyze_button,
             self.export_button]
        ])

    def devalidate(self, start):
        i = self.ordered.index(start)
        for key in self.ordered[i:]:
            self._info_handler.put_field(
                key=key, value=None
            )

    def _sync_button(self, doing=None):
        """
        To sync the state of the button to ensure no accidental error,

        We follow a few rules:
            *-> Before Root Path and Index Path set,
                    Preprocess Button needs to be disabled
            *-> Before Root Path set,
                    Review preprocess button needs to be disabled
            *-> Before Root Path set,
                    Load data Button needs to be disabled
            -> Before article and sorting set,
                    Extraction Button needs to be disabled
            -> Before tags set,
                    Review Extraction Button needs to be disabled
            -> Before tags, article and sorting set,
                    Analyze Button needs to be disabled
            -> Before summary, detail, sorting set,
                    Export Button needs to be disabled
        """
        button_to_enable = []
        if doing is None:
            button_to_enable.append(self.auto_next_step)
            button_to_enable.append(self.show_stat_detail)
            button_to_enable.append(self.preprocess_button)
            button_to_enable.append(self.review_preprocess_button)
            button_to_enable.append(self.load_data_button)
            article = self._info_handler.is_available(INFO_ARTICLES)
            sorting = self._info_handler.is_available(INFO_SORTING)
            tags = self._info_handler.is_available(INFO_TAGS)
            summary = self._info_handler.is_available(INFO_ANALYZED_SUMMARY)
            detail = self._info_handler.is_available(INFO_ANALYZED_DETAIL)
            # we apply the rules
            if article and sorting:
                button_to_enable.append(self.extraction_button)
            if tags:
                button_to_enable.append(self.review_extraction_button)
            if article and sorting and tags:
                button_to_enable.append(self.analyze_button)
            if sorting and summary and detail:
                button_to_enable.append(self.export_button)
        else:
            # disable any button except doing
            button_to_enable.append(doing)
        for b in self._buttons:
            if b in button_to_enable:
                b.config(state=tk.NORMAL)
            else:
                b.config(state=tk.DISABLED)

    def review_preprocess(self):
        self._sync_button(doing=self.review_preprocess_button)
        try:
            data_path = join(self._info_handler.get(INFO_PATH_ROOT),
                             DATA_PATH)
            abs_path = abspath(data_path)
            if not exists(abs_path):
                raise ValueError("根目录没有 data 文件夹! 请先进行预处理，或选择其他根目录！")
            if DEVICE_OS in ["Darwin"]:
                subprocess.Popen(
                    ["open", "-R", "{}".format(abs_path)])
            elif DEVICE_OS in ["Windows"]:
                subprocess.Popen(
                    ["explorer", "{}".format(abs_path)])
            elif DEVICE_OS in ["Linux"]:
                subprocess.Popen(
                    ["nautilus", "--browser", "{}".format(abs_path)])
            else:
                raise Exception(
                    "Not Supported Operating System [{}]!".format(DEVICE_OS))
        except ValueError as v:
            s = str(v)
            self.tracker.log("值错误！ [error='{}']".format(s),
                             tp=TRACKER_LOG_ERROR, exc_info=v, prt=True)
            messagebox.showerror(
                parent=self.master, title="值错误",
                message="值错误！\n"
                        "请检查对应域是否填写错误！\n"
                        "\n"
                        "错误信息:\n{}".format(s))
        except Exception as e:
            s = str(e)
            self.tracker.log("未知错误！ [error='{}']".format(s),
                             tp=TRACKER_LOG_ERROR, exc_info=e, prt=True)
            messagebox.showerror(
                parent=self.master, title="未知错误",
                message="未知错误！\n"
                        "请联系开发者并汇报该错误！\n"
                        "\n"
                        "错误信息:\n{}".format(s))
        finally:
            self._sync_button()

    def review_extraction(self):
        self._sync_button(doing=self.review_extraction_button)
        try:
            segments = self._info_handler.get(INFO_TAGS)
            words = frozenset(
                tag
                for articles in segments.values()
                for article in articles.values()
                for tag in article
            )
            SelectionDialog(
                master=self.master, title="查看 抽取词汇 ({}个)".format(len(words)),
                default_value=sorted(
                    list(words),
                    key=lambda w: pinyin.get(w, format="strip", delimiter=" ")),
                editable=False)
        except ValueError as v:
            s = str(v)
            self.tracker.log("值错误！ [error='{}']".format(s),
                             tp=TRACKER_LOG_ERROR, exc_info=v, prt=True)
            messagebox.showerror(
                parent=self.master, title="值错误",
                message="值错误！\n"
                        "请检查对应域是否填写错误！\n"
                        "\n"
                        "错误信息:\n{}".format(s))
        except Exception as e:
            s = str(e)
            self.tracker.log("未知错误！ [error='{}']".format(s),
                             tp=TRACKER_LOG_ERROR, exc_info=e, prt=True)
            messagebox.showerror(
                parent=self.master, title="未知错误",
                message="未知错误！\n"
                        "请联系开发者并汇报该错误！\n"
                        "\n"
                        "错误信息:\n{}".format(s))
        finally:
            self._sync_button()

    def _starting_preprocess(self):
        # we need to turn other button off to avoid having two process at once
        self._sync_button(doing=self.preprocess_button)
        self.preprocess_button.flip()
        return True

    def _ending_preprocess(self):
        if self._preprocess_thread.get_thread().is_successful():
            # save the necessary data
            # devalidate the data
            self.devalidate(INFO_ARTICLES)
            # continue to next step
            if self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                # don't sync but flip
                self.preprocess_button.flip()
                self.master.after(1000, self._load_data_thread.run, False)
            else:
                # sync and flip
                self._sync_button()
                self.preprocess_button.flip()
        else:
            self._sync_button()
            self.preprocess_button.flip()

    def _starting_load_data(self):
        self._sync_button(doing=self.load_data_button)
        self.load_data_button.flip()
        return True

    def _ending_load_data(self):
        if self._load_data_thread.get_thread().is_successful():
            articles, sorting = self._load_data_thread.get_thread() \
                .get_return_value()
            self._info_handler.put_field(
                key=INFO_ARTICLES, value=articles
            )
            self._info_handler.put_field(
                key=INFO_SORTING, value=sorting
            )
            # devalidate the data
            self.devalidate(INFO_TAGS)
            if self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                # don't sync but flip
                self.load_data_button.flip()
                self.master.after(1000, self._extraction_thread.run, False)
            else:
                self._sync_button()
                self.load_data_button.flip()
        else:
            self._sync_button()
            self.load_data_button.flip()

    def _starting_extraction(self):
        self._sync_button(doing=self.extraction_button)
        self.extraction_button.flip()
        return True

    def _ending_extraction(self):
        if self._extraction_thread.get_thread().is_successful():
            segments = self._extraction_thread.get_thread().get_return_value()
            self._info_handler.put_field(
                key=INFO_TAGS, value=segments
            )
            # devalidate the data
            self.devalidate(INFO_ANALYZED_SUMMARY)
            if self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                self.extraction_button.flip()
                self.master.after(1000, self._analyze_thread.run, False)
            else:
                self._sync_button()
                self.extraction_button.flip()
        else:
            self._sync_button()
            self.extraction_button.flip()

    def _starting_analyze(self):
        self._sync_button(doing=self.analyze_button)
        self.analyze_button.flip()
        return True

    def _ending_analyze(self):
        if self._analyze_thread.get_thread().is_successful():
            summary, detail = self._analyze_thread.get_thread() \
                .get_return_value()
            self._info_handler.put_field(
                key=INFO_ANALYZED_SUMMARY, value=summary
            )
            self._info_handler.put_field(
                key=INFO_ANALYZED_DETAIL, value=detail
            )
            self._sync_button()
            self.analyze_button.flip()
        else:
            self._sync_button()
            self.analyze_button.flip()

    def _starting_export(self):
        path = ask_save_file(master=self.master.master,
                             title="选择输出地址",
                             filetypes=(FILE_TYPE_EXCEL,),
                             initdir=self.export_path)
        if not path:
            return False
        self.export_path, _ = split(path)
        self._info_handler.put_field(key=INFO_OUTPUT_PATH, value=path)
        self._sync_button(doing=self.analyze_button)
        self.analyze_button.flip()
        return True

    def _ending_export(self):
        self._sync_button()
        self.analyze_button.flip()


class RightJiebaOpFrame(LabeledBaseFrame):
    """
    [ LabelScalePair ] 2
    [ RadioButtonPair ] 2
    [ Checkbox ] 1
    ===========
    Jieba Optimization Field:
        Num wanted              Slider                  LabelScalePair
        Extractor selection     Selection               RadioButtonPair
        Use HMM                 Checkbox
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "jieba 优化", size_conf, info_handler)
        self._num_wanted = None
        self._extractor_select = None
        self.add_items()
        self.place_items()
        self._info_handler.register_field(
            source=self._num_wanted,
            default=0,
            key=INFO_ANALYZE_NUM_WANTED,
            not_none=True, type_=int
        )
        self._info_handler.register_field(
            source=self._extractor_select,
            default=TF_IDF,
            key=INFO_ANALYZE_EXTRACTOR,
            not_none=True
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True, height_offset=21,
            width_offset=4)
        self._num_wanted = LabelScalePair(
            master=self, label_text="抽取词汇数目",
            from_=0, to_=1000, size_conf=divided[0][0]
        )
        self._extractor_select = RadioButtonsPair(
            master=self, label_text="选择 高频词汇抽取器",
            options=[
                ("TF-IDF", TF_IDF),
                ("TextRank", TEXT_RANK),
            ],
            var=tk.StringVar,
            size_conf=divided[1][0],
        )

    def place_items(self):
        self.size_conf.place([
            [self._num_wanted],
            [self._extractor_select],
        ])


class RightWordEditFrame(LabeledBaseFrame):
    """
    [ EditField ] [ EditField ]
    [ EditField ] [ EditField ]
    ================
    Word Editor Field:
        Allow poss              Button Separate Dialog
        Suggestion word         Button Separate Dialog
        Whitelist word          Button Separate Dialog
        Blacklist word          Button Separate Dialog
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "词汇编辑", size_conf, info_handler)
        self.edit_allow_pos = None
        self.edit_suggestion_word = None
        self.edit_whitelist_word = None
        self.edit_blacklist_word = None
        self.add_items()
        self.place_items()
        self._info_handler.register_field(
            source=self.edit_allow_pos,
            default=DEFAULT_POS,
            key=INFO_ANALYZE_ALLOW_POS,
            not_none=True, type_=list
        )
        self._info_handler.register_field(
            source=self.edit_suggestion_word,
            default=[],
            key=INFO_ANALYZE_SUGGESTION_WORD,
            not_none=True, type_=list
        )
        self._info_handler.register_field(
            source=self.edit_whitelist_word,
            default=[],
            key=INFO_ANALYZE_WHITELIST_WORD,
            not_none=True, type_=list
        )
        self._info_handler.register_field(
            source=self.edit_blacklist_word,
            default=[],
            key=INFO_ANALYZE_BLACKLIST_WORD,
            not_none=True, type_=list
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1, 1),
            (1, 1, 1),
        ), spacing=DEFAULT_SPACING, internal=True, height_offset=21,
            width_offset=4)
        self.edit_allow_pos = EditFieldPair(
            master=self, name="词性筛选", size_conf=divided[0][0],
            options=POS_OPTIONS
        )
        self.edit_suggestion_word = EditFieldPair(
            master=self, name="建议词汇", size_conf=divided[0][1]
        )
        self.edit_whitelist_word = EditFieldPair(
            master=self, name="白名单词汇", size_conf=divided[1][0]
        )
        self.edit_blacklist_word = EditFieldPair(
            master=self, name="黑名单词汇", size_conf=divided[1][1]
        )

    def place_items(self):
        self.size_conf.place([
            [self.edit_allow_pos,
             self.edit_suggestion_word],
            [self.edit_whitelist_word,
             self.edit_blacklist_word],
        ])


class RightStatAnalyzerFrame(LabeledBaseFrame):
    """
    [ RadioButtonPart ] 1
    ===========
    Stat Analyzer Field:
        Stats Analyzer          Selection               RadioButtonPart
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "统计分析器", size_conf, info_handler)
        self.select_stat_analyze = None
        self.add_items()
        self.place_items()
        self._info_handler.register_field(
            source=self.select_stat_analyze,
            default=TREND_ANALYZER,
            key=INFO_ANALYZE_STAT_ANALYZER,
            not_none=True
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True, height_offset=21,
            width_offset=4)
        self.select_stat_analyze = RadioButtonsPair(
            master=self, label_text="选择 统计分析器",
            options=[
                ("趋势分析器", TREND_ANALYZER),
            ],
            var=tk.StringVar,
            size_conf=divided[0][0]
        )

    def place_items(self):
        self.size_conf.place([
            [self.select_stat_analyze],
        ])
