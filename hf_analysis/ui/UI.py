import subprocess
import tkinter.messagebox as messagebox
from tkinter.ttk import Progressbar

import pinyin

from hf_analysis.ui.tk_object import *
from hf_analysis.word.word_analysis import TEXT_RANK, TF_IDF


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


class MainApplication:
    def __init__(self, tk_instance, info_handler,
                 title="HF Word Analysis", width=700, height=800):
        self.root = tk_instance
        self.root.minsize(width, height)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x, y = (screen_width - width) // 2, (screen_height - height) // 2
        self.root.geometry("+{}+{}".format(x, y))
        self.size = width, height
        self.root.title(title)
        self.root.resizable(0, 0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        # size_config
        self.size_config = TopDownSizeConfig(width, height)
        divided = self.size_config.divide(((1, 1),), 0, False)
        self.infoFrame = InfoFrame(
            master=self.root, size_conf=divided[0][0], info_handler=info_handler
        )
        self.infoFrame.pack(side=tk.TOP)

    def on_exit(self):
        self.infoFrame.on_exit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def get_tracker(self):
        return self.infoFrame.tracker


class InfoFrame(tk.Frame):
    def __init__(self, master, size_conf, info_handler):
        width, height = size_conf.total_size()
        super().__init__(master, width=width, height=height)
        self.size_conf = size_conf
        self.tk_frame = master
        self.tracker = ProgressTracker(
            enable_print_out=True,
            update_func=self.tracker_listener
        )
        self.left_pram_frame = None
        self.right_pram_frame = None
        self.central_frame = None
        self.status_bar_frame = None
        # information handler
        self._info_handler = info_handler
        self.add_items()
        self.place_item()
        # try to load from JSON
        self._info_handler.load_from_json(tracker=self.tracker)
        self._info_handler.sync_all()

    def add_items(self):
        divided = self.size_conf.divide((
            (29, 1, 1),  # the main section
            (10, 1),  # the action center
            (1, 1)  # the status bar
        ), spacing=5, internal=False)
        self.left_pram_frame = LeftPramFrame(
            master=self, size_conf=divided[0][0],
            info_handler=self._info_handler
        )
        self.central_frame = CentralFrame(
            master=self, size_config=divided[1][0], tracker=self.tracker,
            info_handler=self._info_handler
        )
        self.right_pram_frame = RightPramFrame(
            master=self, size_config=divided[0][1],
            info_handler=self._info_handler
        )
        self.status_bar_frame = StatusBarFrame(
            master=self, size_config=divided[2][0],
            info_handler=self._info_handler
        )

    def place_item(self):
        self.size_conf.place([
            [self.left_pram_frame, self.right_pram_frame],
            [self.central_frame],
            [self.status_bar_frame],
        ])

    def on_exit(self):
        self._info_handler.write_to_json(
            tracker=self.tracker, exclude=(
                INFO_LOADER_RAW_DATA,
                INFO_EXTRACTOR_SEGMENTS,
                INFO_ANALYZED_DATA
            ))
        self.tracker.log("Exiting Application...")

    def tracker_listener(self, *args, **kwargs):
        mode = kwargs["mode"]
        if mode in [TRACKER_TICK, TRACKER_TICK_INIT, TRACKER_PARENT_INIT,
                    TRACKER_PARENT_TICK]:
            self.central_frame.progress_update(*args, **kwargs)
        elif mode in [TRACKER_LOG]:
            self.status_bar_frame.status_bar_update(*args, **kwargs)


class LeftPramFrame(BaseFrame):
    """
    [ File Selection Field ] 4
    [ PDF Selection Field ] 5
    [ OCR Optimization Field ] 1
    ====
    File Selection Field:
        Index Input             File Select             ButtonLabelPair
        Additional Pram Input   File Select             ButtonLabelPair
        Root Directory          Directory Select        ButtonLabelPair
    PDF Field:
        Engine                  pdftoppm / pdftocairo   ChoicePair
        PDF Scan Format         jpeg / tiff / png       ChoicePair
        DPI Field               300 ~ 600               ChoicePair
    OCR Optimization Field:
        Default language        Text Input              LabelEntryButtonPair
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, size_conf, info_handler)
        # File selection field
        self.file_selection_field = None
        # pdf field
        self.pdf_field = None
        # OCR Optimization field
        self.ocr_po_field = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (3, 1),
            (6, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.file_selection_field = LeftFileSelectFrame(
            master=self, size_conf=divided[0][0],
            info_handler=self._info_handler
        )
        self.pdf_field = LeftPdfFrame(
            master=self, size_conf=divided[1][0],
            info_handler=self._info_handler
        )
        self.ocr_po_field = LeftOCROpFrame(
            master=self, size_conf=divided[2][0],
            info_handler=self._info_handler
        )

    def place_items(self):
        self.size_conf.place([
            [self.file_selection_field],
            [self.pdf_field],
            [self.ocr_po_field],
        ])


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
            mandatory_field=False
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
        self.select_pdf_engine = RadioButtonPair(
            master=self, label_text="选择 PDF 处理引擎", options=[
                ("pdftoppm", PDF_ENGINE_PDFTOPPM),
                ("pdftocairo", PDF_ENGINE_PDFTOCAIRO)
            ],
            var=tk.BooleanVar,
            size_conf=divided[0][0]
        )
        self.select_pdf_scan_format = RadioButtonPair(
            master=self, label_text="选择 PDF 扫描格式", options=[
                ("jpg (推荐)", "jpg"),
                ("png", "png"),
                ("tiff", "tiff"),
            ],
            var=tk.StringVar,
            size_conf=divided[1][0]
        )
        self.select_pdf_dpi = RadioButtonPair(
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
    [ LabelEntryPair ]
    ======
    OCR Optimization Field:
        Default language        Text Input              LabelEntryButtonPair
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "OCR 优化", size_conf, info_handler)
        self.input_default_language = None
        self.add_items()
        self.place_items()
        # register field
        self._info_handler.register_field(
            self.input_default_language, key=INFO_OCR_DEF_LANG,
            default="chi_sim",
            not_none=True,
            not_empty=True,
            type_=str
        )

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.input_default_language = LabelEntryPair(
            master=self, label_text="默认语言",
            button_text="？", button_func=self.show_available_lang,
            size_conf=divided[0][0]
        )

    def place_items(self):
        self.size_conf.place([
            [self.input_default_language],
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


class CentralFrame(BaseFrame):
    """
    [ Instruction Field ]
    [ Progress Field ]
    [ Action Field ]
    ====
    Instruction Field:
        Label                   Label                   Label
    Progress Field:
        Label                   Label                   Label
        Progressbar             Progress Bar            Progress Bar
    Action Field:
        Prepare Data            Button                  Button
        Process Data            Button                  Button
        Export Data             Button                  Button
   """

    def __init__(self, master, size_config, tracker, info_handler):
        super().__init__(master, size_config, info_handler)
        self.instruction_field = None
        self.progress_field = None
        self.action_field = None
        self.tracker = tracker
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            # (10, 1),
            (3, 1),
            (2, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        # self.instruction_field = CentralInstructionFrame(
        #     master=self, size_config=divided[0][0],
        #     info_handler=self._info_handler
        # )
        self.progress_field = CentralProgressBarFrame(
            master=self, size_config=divided[0][0],
            info_handler=self._info_handler
        )
        self.action_field = CentralActionFrame(
            master=self, size_config=divided[1][0], tracker=self.tracker,
            info_handler=self._info_handler
        )

    def place_items(self):
        self.size_conf.place([
            # [self.instruction_field],
            [self.progress_field],
            [self.action_field],
        ])

    def progress_update(self, *args, **kwargs):
        self.progress_field.progress_update(*args, **kwargs)


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
    [ progressbar ]
    """

    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.label_var = None
        self.progress_total_var = None
        self.progress_current_var = None
        self.progress_label = None
        self.progress_bar_total = None
        self.progress_bar_current = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 1),
            (1, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.label_var = tk.StringVar()
        self.label_var.set("欢迎！")
        self.progress_total_var = tk.IntVar()
        self.progress_current_var = tk.IntVar()
        self.progress_label = tk.Label(master=self, textvariable=self.label_var,
                                       anchor=tk.CENTER)
        self.progress_bar_current = Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            mode="determinate",
            variable=self.progress_current_var
        )
        self.progress_bar_total = Progressbar(
            master=self,
            orient=tk.HORIZONTAL,
            mode="determinate",
            variable=self.progress_total_var
        )

    def place_items(self):
        self.size_conf.place([
            [self.progress_label],
            [self.progress_bar_current],
            [self.progress_bar_total],
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
                self.label_var.set("结束!")
            else:
                message = "{} {} 预计剩余: {}".format(
                    process_disc,
                    (disc_fill if disc_fill is not None else
                     "({}/{})".format(current_tick, total_tick)),
                    time_remain
                )
                self.label_var.set(message)
        elif mode == TRACKER_PARENT_INIT:
            total_tick = kwargs["total_tick"]
            init_tick = kwargs["init_tick"]
            self.progress_bar_total["maximum"] = total_tick
            self.progress_total_var.set(init_tick)
        elif mode == TRACKER_PARENT_TICK:
            current_tick = kwargs["current_tick"]
            self.progress_total_var.set(current_tick)


class CentralActionFrame(BaseFrame):
    """
    [ button, button, button ]
    """

    def __init__(self, master, size_config, tracker, info_handler):
        super().__init__(master, size_config, info_handler)
        self.auto_next_step = None
        self.preprocess_button = None
        self.review_preprocess_button = None
        self.load_data_button = None
        self.extraction_button = None
        self.review_extraction_button = None
        self.analyze_button = None
        self.export_button = None
        self._buttons = None
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
        # start
        self.add_items()
        self.place_items()
        self.ordered = [
            INFO_LOADER_RAW_DATA,
            INFO_EXTRACTOR_SEGMENTS,
            INFO_ANALYZED_DATA,
        ]
        self._info_handler.register_field(
            source=self.auto_next_step,
            default=True,
            key=INFO_ACTION_AUTO_NEXT_STEP,
            type_=bool
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            not_empty=True,
            key=INFO_LOADER_RAW_DATA,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            not_empty=True,
            key=INFO_EXTRACTOR_SEGMENTS,
        )
        self._info_handler.register_field(
            source=None,
            default=None,
            not_none=True,
            not_empty=True,
            key=INFO_ANALYZED_DATA,
        )
        self._sync_button()

    def add_items(self, *args, **kwargs):
        divide = self.size_conf.divide((
            (1, 3, 1, 1),
            (2, 3, 3, 3, 3, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.auto_next_step = CheckButtonPair(
            master=self, text="自动开始下一步骤", size_conf=divide[0][0], anchor=tk.W
        )
        self.preprocess_button = TwoStageButton(
            master=self, command=self._preprocess_thread.run,
            text_choice={True: "预处理", False: "预处理中..."},
            init_pos=True
        )
        self.review_preprocess_button = tk.Button(
            master=self, command=self.review_preprocess,
            text="查看 预处理成果"
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
            text="查看 抽取成果"
        )
        self.analyze_button = TwoStageButton(
            master=self, command=self._analyze_thread.run,
            text_choice={True: "统计分析", False: "统计分析中..."},
            init_pos=True
        )
        self.export_button = tk.Button(
            master=self, command=self.export,
            text="输出", fg="red"
        )
        self._buttons = [
            self.auto_next_step,
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
            [self.auto_next_step, self.review_preprocess_button,
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
            -> Before RAW DATA set,
                    Extraction Button needs to be disabled
            -> Before Segments set,
                    Review Extraction Button needs to be disabled
            -> Before Segments set,
                    Analyze Button needs to be disabled
            -> Before Analyzed Data set,
                    Export Button needs to be disabled
        """
        button_to_enable = []
        if doing is None:
            button_to_enable.append(self.auto_next_step)
            button_to_enable.append(self.preprocess_button)
            button_to_enable.append(self.review_preprocess_button)
            button_to_enable.append(self.load_data_button)
            raw_data = self._info_handler.is_available(INFO_LOADER_RAW_DATA)
            segments = self._info_handler.is_available(INFO_EXTRACTOR_SEGMENTS)
            analyzed = self._info_handler.is_available(INFO_ANALYZED_DATA)
            # we apply the rules
            if raw_data:
                button_to_enable.append(self.extraction_button)
            if segments:
                button_to_enable.extend([
                    self.review_extraction_button,
                    self.analyze_button,
                ])
            if analyzed:
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
            segments = self._info_handler.get(INFO_EXTRACTOR_SEGMENTS)
            words = frozenset(
                word for articles, _, _ in segments for article in
                articles.values() for word in article
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

    def _ending_preprocess(self):
        if self._preprocess_thread.get_thread().is_successful():
            # save the necessary data
            # devalidate the data
            self.devalidate(INFO_LOADER_RAW_DATA)
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

    def _ending_load_data(self):
        if self._load_data_thread.get_thread().is_successful():
            raw_data = self._load_data_thread.get_thread().get_return_value()
            self._info_handler.put_field(
                key=INFO_LOADER_RAW_DATA, value=raw_data
            )
            # devalidate the data
            self.devalidate(INFO_EXTRACTOR_SEGMENTS)
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

    def _ending_extraction(self):
        if self._extraction_thread.get_thread().is_successful():
            segments = self._extraction_thread.get_thread().get_return_value()
            self._info_handler.put_field(
                key=INFO_EXTRACTOR_SEGMENTS, value=segments
            )
            # devalidate the data
            self.devalidate(INFO_ANALYZED_DATA)
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

    def _ending_analyze(self):
        if self._analyze_thread.get_thread().is_successful():
            analyzed_data = self._analyze_thread.get_thread().get_return_value()
            self._info_handler.put_field(
                key=INFO_ANALYZED_DATA, value=analyzed_data
            )
            self._sync_button()
            self.analyze_button.flip()
        else:
            self._sync_button()
            self.analyze_button.flip()

    def export(self):
        self._sync_button(doing=self.export_button)
        self._sync_button()


class RightPramFrame(BaseFrame):
    """
    [ Jieba Optimization Field ]
    [ Word Editor Field ]
    [ Stat Analyzer Field ]
    ====
    Jieba Optimization Field:
        Num wanted              Slider                  LabelScalePair
        Extractor selection     Selection               RadioButtonPair
    Word Editor Field:
        Suggestion word         Button Separate Dialog
        Whitelist word          Button Separate Dialog
        Blacklist word          Button Separate Dialog
    Stat Analyzer Field:
        Stats Analyzer          Selection               RadioButtonPart
    """

    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.jieba_op_field = None
        self.word_editor_field = None
        self.stat_analyzer_field = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (4, 1),
            (6, 1),
            (2, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.jieba_op_field = RightJiebaOpFrame(
            master=self, info_handler=self._info_handler,
            size_conf=divided[0][0]
        )
        self.word_editor_field = RightWordEditFrame(
            master=self, info_handler=self._info_handler,
            size_conf=divided[1][0]
        )
        self.stat_analyzer_field = RightStatAnalyzerFrame(
            master=self, info_handler=self._info_handler,
            size_conf=divided[2][0]
        )

    def place_items(self):
        self.size_conf.place([
            [self.jieba_op_field],
            [self.word_editor_field],
            [self.stat_analyzer_field],
        ])


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
            from_=0, to_=100, size_conf=divided[0][0]
        )
        self._extractor_select = RadioButtonPair(
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
    [ EditField ] [ EditField ] [ EditField ]
    ================
    Word Editor Field:
        Suggestion word         Button Separate Dialog
        Whitelist word          Button Separate Dialog
        Blacklist word          Button Separate Dialog
    """

    def __init__(self, master, size_conf, info_handler):
        super().__init__(master, "词汇编辑", size_conf, info_handler)
        self.edit_suggestion_word = None
        self.edit_whitelist_word = None
        self.edit_blacklist_word = None
        self.add_items()
        self.place_items()
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
            (1, 1, 1, 1),
        ), spacing=DEFAULT_SPACING, internal=True, height_offset=21,
            width_offset=4)
        self.edit_suggestion_word = EditFieldPair(
            master=self, name="建议词汇", size_conf=divided[0][0]
        )
        self.edit_whitelist_word = EditFieldPair(
            master=self, name="白名单词汇", size_conf=divided[0][1]
        )
        self.edit_blacklist_word = EditFieldPair(
            master=self, name="黑名单词汇", size_conf=divided[0][2]
        )

    def place_items(self):
        self.size_conf.place([
            [self.edit_suggestion_word, self.edit_whitelist_word,
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
        self.select_stat_analyze = RadioButtonPair(
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


class StatusBarFrame(BaseFrame):
    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.status_bar = None
        self.status_bar_var = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 1),
        ), spacing=0, internal=True)
        self.status_bar_var = tk.StringVar()
        self.status_bar_var.set("欢迎！")
        self.status_bar = tk.Label(
            self, relief=tk.SUNKEN, anchor=tk.W,
            textvariable=self.status_bar_var
        )

    def place_items(self):
        self.size_conf.place([
            [self.status_bar],
        ])

    def status_bar_update(self, **kwargs):
        prt = kwargs["prt"]
        if not prt:
            return
        log_type = kwargs["tp"]
        log_message = kwargs["message"]
        if log_type in [TRACKER_LOG_INFO]:
            log_prefix = ""
        elif log_type in [TRACKER_LOG_ERROR]:
            log_prefix = "[ERROR]"
        else:
            log_prefix = ""
        self.status_bar_var.set("{}{}".format(log_prefix, log_message))
