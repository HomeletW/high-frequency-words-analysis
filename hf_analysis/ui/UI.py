from ui.parm_field import *


class MainApplication:
    def __init__(self, tk_instance, info_handler,
                 title="HF Word Analysis", width=690, height=780):
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
            (23, 6, 4),  # the main section
            (6, 1),  # the action center
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
                INFO_ARTICLES,
                INFO_SORTING,
                INFO_TAGS,
                INFO_ANALYZED_SUMMARY,
                INFO_ANALYZED_DETAIL,
                INFO_PATCH,
            ))
        self.tracker.log("Exiting Application...")

    def tracker_listener(self, *args, **kwargs):
        mode = kwargs["mode"]
        if mode in [TRACKER_TICK, TRACKER_TICK_INIT, TRACKER_TICK_DESC_UPDATE,
                    TRACKER_SET_INDETERMINATE]:
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
            (4, 1),
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
            (2, 1),
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
            (9, 1),
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


class StatusBarFrame(BaseFrame):
    def __init__(self, master, size_config, info_handler):
        super().__init__(master, size_config, info_handler)
        self.status_bar_var = None
        self.status_bar = None
        self.patch_label = None
        self.add_items()
        self.place_items()

    def add_items(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 28, 2),
        ), spacing=0, internal=True)
        self.status_bar_var = tk.StringVar()
        self.status_bar_var.set("欢迎！")
        self.status_bar = tk.Label(
            self, relief=tk.SUNKEN, anchor=tk.W,
            textvariable=self.status_bar_var
        )
        self.patch_label = tk.Label(
            self, anchor=tk.E,
            text=self._info_handler.get(INFO_PATCH)
        )

    def place_items(self):
        self.size_conf.place([
            [self.status_bar, self.patch_label],
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
