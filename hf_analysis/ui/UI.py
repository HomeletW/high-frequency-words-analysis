import tkinter.messagebox as messagebox
from tkinter.ttk import Progressbar

from hf_analysis.ui.tk_object import *


class BaseFrame(tk.Frame, Sizeable):
    def __init__(self, master, size_conf):
        width, height = size_conf.total_size()
        super().__init__(master, width=width, height=height)
        self.size_conf = size_conf

    def add_item(self, *args, **kwargs):
        raise NotImplementedError

    def place_item(self):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()


class LabeledBaseFrame(tk.LabelFrame, Sizeable):
    def __init__(self, master, text, size_conf):
        width, height = size_conf.total_size()
        super().__init__(master, text=text, width=width, height=height)
        self.size_conf = size_conf

    def add_item(self, *args, **kwargs):
        raise NotImplementedError

    def place_item(self):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()


class Main:
    def __init__(self, title="HF Word Analysis", width=1500, height=600):
        self.root = tk.Tk()
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
            master=self.root, size_conf=divided[0][0]
        )
        self.infoFrame.pack(side=tk.TOP)

    def on_exit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


class InfoFrame(tk.Frame):
    def __init__(self, master, size_conf):
        width, height = size_conf.total_size()
        super().__init__(master, width=width, height=height)
        self.size_conf = size_conf
        self.tk_frame = master
        self.tracker = ProgressTracker(
            enable_print_out=True,
            update_func=self.tracker_listener
        )
        self.preprocess_pram_frame = None
        self.other_pram_frame = None
        self.central_frame = None
        self.status_bar_frame = None
        self.add_items()
        self.place_item()

    def add_items(self):
        divided = self.size_conf.divide((
            (29, 1, 2, 1),  # the main section
            (1, 1)  # the status bar
        ), spacing=DEFAULT_SPACING, internal=False)
        self.preprocess_pram_frame = PreprocessPramFrame(
            master=self, size_conf=divided[0][0]
        )
        self.central_frame = CentralFrame(
            master=self, size_config=divided[0][1], tracker=self.tracker
        )
        self.status_bar_frame = StatusBarFrame(
            master=self, size_config=divided[1][0]
        )

    def place_item(self):
        self.size_conf.place([
            [self.preprocess_pram_frame, self.central_frame, None],
            [self.status_bar_frame],
        ])

    def tracker_listener(self, *args, **kwargs):
        mode = kwargs["mode"]
        if mode in [TRACKER_TICK, TRACKER_TICK_INIT, TRACKER_PARENT_INIT,
                    TRACKER_PARENT_TICK]:
            self.central_frame.progress_update(*args, **kwargs)
        elif mode in [TRACKER_LOG]:
            self.status_bar_frame.status_bar_update(*args, **kwargs)


class PreprocessPramFrame(BaseFrame):
    """
    [ File Selection Field ] 3
    [ PDF Selection Field ] 6
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

    def __init__(self, master, size_conf):
        super().__init__(master, size_conf)
        # File selection field
        self.file_selection_field = None
        # pdf field
        self.pdf_field = None
        # OCR Optimization field
        self.ocr_po_field = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (3, 1),
            (6, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=False)
        self.file_selection_field = PreprocessFileSelectFrame(
            master=self, size_conf=divided[0][0]
        )
        self.pdf_field = PreprocessPdfFrame(
            master=self, size_conf=divided[1][0]
        )
        self.ocr_po_field = PreprocessOCROpFrame(
            master=self, size_conf=divided[2][0]
        )

    def place_item(self):
        self.size_conf.place([
            [self.file_selection_field],
            [self.pdf_field],
            [self.ocr_po_field],
        ])


class PreprocessFileSelectFrame(LabeledBaseFrame):
    """
    [ ButtonLabelPair ] 1
    [ ButtonLabelPair ] 1
    [ ButtonLabelPair ] 1
    """

    def __init__(self, master, size_conf):
        super().__init__(master, "文件选择", size_conf)
        self.open_root_directory = None
        self.open_index_file = None
        self.open_add_pram_file = None
        self.index_file = None
        self.add_pram_file = None
        self.root_directory = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
            (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.open_root_directory = ButtonLabelPair(
            master=self, button_text="选择 根目录",
            button_func=self.open_directory,
            label_text="-", size_conf=divided[2][0]
        )
        self.open_index_file = ButtonLabelPair(
            master=self, button_text="选择 索引文件",
            button_func=self.open_index,
            label_text="-", size_conf=divided[0][0]
        )
        self.open_add_pram_file = ButtonLabelPair(
            master=self, button_text="选择 附加参数文件",
            button_func=self.open_additional_parm,
            label_text="-", size_conf=divided[1][0]
        )
        self.open_root_directory.set_button_fg("red")
        self.open_index_file.set_button_fg("red")
        self.open_add_pram_file.set_button_fg("red")

    def place_item(self):
        self.size_conf.place((
            [self.open_root_directory],
            [self.open_index_file],
            [self.open_add_pram_file],
        ))

    def open_index(self):
        if self.index_file is not None and self.index_file != "":
            initdir = self.index_file
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_file(self, "选择 索引文件", (FILE_TYPE_EXCEL,),
                                initdir=initdir)
        if ret_dir == "":
            return
        self.index_file = ret_dir
        self.open_index_file.set_info(ret_dir)
        self.open_index_file.set_button_fg("black")

    def open_additional_parm(self):
        if self.add_pram_file is not None and self.add_pram_file != "":
            initdir = self.index_file
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_file(self, "选择 附加参数文件",
                                (FILE_TYPE_EXCEL,), initdir=initdir)
        if ret_dir == "":
            return
        self.add_pram_file = ret_dir
        self.open_add_pram_file.set_info(ret_dir)
        self.open_add_pram_file.set_button_fg("black")

    def open_directory(self):
        if self.root_directory is not None and self.root_directory != "":
            initdir = self.index_file
        else:
            initdir = DEFAULT_DIR
        ret_dir = ask_open_directory(self, "选择 根目录", initdir=initdir)
        if ret_dir == "":
            return
        self.root_directory = ret_dir
        self.open_root_directory.set_info(ret_dir)
        self.open_root_directory.set_button_fg("black")


class PreprocessPdfFrame(LabeledBaseFrame):
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

    def __init__(self, master, size_conf):
        super().__init__(master, "PDF 处理", size_conf)
        self.select_pdf_engine = None
        self.select_pdf_scan_format = None
        self.select_pdf_dpi = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
            (1, 1),
            (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.select_pdf_engine = RadioButtonPair(
            master=self, label_text="选择 PDF 处理引擎", variables=[
                ("pdftoppm", "pdftoppm"),
                ("pdftocairo", "pdftocairo")
            ], default_value=0,
            size_conf=divided[0][0]
        )
        self.select_pdf_scan_format = RadioButtonPair(
            master=self, label_text="选择 PDF 扫描格式", variables=[
                ("jpeg (推荐)", "jpeg"),
                ("png", "png"),
                ("tiff", "tiff"),
            ], default_value=0,
            size_conf=divided[1][0]
        )
        self.select_pdf_dpi = RadioButtonPair(
            master=self, label_text="选择 PDF 扫描DPI (速度快 - 效果清晰)", variables=[
                ("300", "300"),
                ("400", "400"),
                ("500", "500"),
                ("600", "600"),
            ], default_value=0,
            size_conf=divided[2][0]
        )

    def place_item(self):
        self.size_conf.place((
            [self.select_pdf_engine],
            [self.select_pdf_scan_format],
            [self.select_pdf_dpi]
        ))

    def get_pdf_engine(self):
        return self.select_pdf_engine.get_info()

    def get_pdf_scan_format(self):
        return self.select_pdf_scan_format.get_info()

    def get_pdf_dpi(self):
        return self.select_pdf_dpi.get_info()


class PreprocessOCROpFrame(LabeledBaseFrame):
    """
    [ LabelEntryPair ]
    ======
    OCR Optimization Field:
        Default language        Text Input              LabelEntryButtonPair
    """

    def __init__(self, master, size_conf):
        super().__init__(master, "OCR 优化", size_conf)
        self.input_default_language = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (1, 1),
        ), spacing=0, internal=True, height_offset=20, width_offset=4)
        self.input_default_language = LabelEntryPair(
            master=self, label_text="默认语言", entry_placeholder="chi_sim",
            button_text="？", button_func=self.show_available_lang,
            size_conf=divided[0][0]
        )

    def place_item(self):
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

    def get_default_lang(self):
        return self.input_default_language.get()


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

    def __init__(self, master, size_config, tracker):
        super().__init__(master, size_config)
        self.instruction_field = None
        self.progress_field = None
        self.action_field = None
        self.tracker = tracker
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        divided = self.size_conf.divide((
            (7, 1),
            (2, 1),
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=False)
        self.instruction_field = CentralInstructionFrame(
            master=self, size_config=divided[0][0]
        )
        self.progress_field = CentralProgressBarFrame(
            master=self, size_config=divided[1][0]
        )
        self.action_field = CentralActionFrame(
            master=self, size_config=divided[2][0], tracker=self.tracker
        )

    def place_item(self):
        self.size_conf.place([
            [self.instruction_field],
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

    def __init__(self, master, size_config):
        super().__init__(master, size_config)
        self.top_label = None
        self.bot_label = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        self.size_conf.divide((
            (2, 1),
            (3, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.top_label = tk.Label(master=self, text="image here")
        self.bot_label = tk.Label(master=self, text="instruction here")

    def place_item(self):
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

    def __init__(self, master, size_config):
        super().__init__(master, size_config)
        self.label_var = None
        self.progress_total_var = None
        self.progress_current_var = None
        self.progress_label = None
        self.progress_bar_total = None
        self.progress_bar_current = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
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

    def place_item(self):
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
            self.progress_current_var.set(current_tick)
            if end:
                self.label_var.set("结束!")
            else:
                self.label_var.set(
                    process_disc + " ({}/{})".format(current_tick, total_tick))
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

    def __init__(self, master, size_config, tracker):
        super().__init__(master, size_config)
        self.preprocess_button = None
        self.load_data_button = None
        self.analyze_button = None
        self.export_button = None
        self.tracker = tracker
        # threading
        self._active_process = []
        self._preprocess_process = None
        # self._load_data_thread = None
        self._analyze_process = None
        # self._export_thread = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 3, 3, 3, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.preprocess_button = TwoStageButton(
            master=self, command=self.preprocess,
            text_choice={True: "预处理", False: "预处理中..."},
            init_pos=True
        )
        self.load_data_button = tk.Button(
            master=self, command=self.load_data,
            text="装载数据"
        )
        self.analyze_button = TwoStageButton(
            master=self, command=self.analyze,
            text_choice={True: "抽取词汇", False: "抽取词汇中..."},
            init_pos=True
        )
        self.export_button = tk.Button(
            master=self, command=self.export,
            text="输出"
        )

    def place_item(self):
        self.size_conf.place([
            [self.preprocess_button, self.load_data_button, self.analyze_button,
             self.export_button]
        ])

    @staticmethod
    def _disable_buttons(button_to_disable):
        for button in button_to_disable:
            button["state"] = tk.DISABLED

    @staticmethod
    def _enable_buttons(button_to_enable):
        for button in button_to_enable:
            button["state"] = tk.NORMAL

    def check_preprocess_process(self):
        if self._preprocess_process is not None:
            if self._preprocess_process.is_finished():
                self._preprocess_process.join()
                self._ending_preprocess()
                self._preprocess_process = None
            else:
                self.master.after(100, self.check_preprocess_process)

    def preprocess(self):
        if self._preprocess_process is None:
            # if no such process is running, we ask user if we can create one
            ret = tk.messagebox.askyesnocancel(parent=self.master,
                                               title="确认",
                                               message="您确定要进行 预处理 么？\n"
                                                       "这需要很长时间, 且一旦开始不可停止.")
            if ret is None or not ret:
                return
            self._preprocess_process = PreprocessProcess(
                "./data/debug_index.xlsx",
                "./data/additioanl_pram.xlsx",
                "./data",
                300,
                "chi_sim", self.tracker
            )
            self._starting_preprocess()
            self._preprocess_process.start()
            self.master.after(100, self.check_preprocess_process)
        else:
            # if there is something running, we let user wait
            tk.messagebox.showwarning(parent=self.master,
                                      title="请稍候",
                                      message="数据预处理中，请稍候...")

    def _starting_preprocess(self):
        # we need to turn other button off to avoid having two process at once
        self._disable_buttons(
            [self.load_data_button, self.analyze_button, self.export_button])
        self.preprocess_button.flip()

    def _ending_preprocess(self):
        # we need to turn other button back on
        self._enable_buttons(
            [self.load_data_button, self.analyze_button, self.export_button])
        self.preprocess_button.flip()

    def load_data(self):
        pass

    def check_analyze_process(self):
        if self._analyze_process is not None:
            if self._analyze_process.is_finished():
                self._analyze_process.join()
                self._analyze_process = None
            else:
                self.master.after(1000, self.check_analyze_process)

    def analyze(self):
        pass

    def export(self):
        pass


class OtherPramFrame(BaseFrame):
    def __init__(self, master, size_config):
        super().__init__(master, size_config)

    def add_item(self, *args, **kwargs):
        pass

    def place_item(self):
        pass


class StatusBarFrame(BaseFrame):
    def __init__(self, master, size_config):
        super().__init__(master, size_config)
        self.status_bar = None
        self.status_bar_var = None
        self.add_item()
        self.place_item()

    def add_item(self, *args, **kwargs):
        self.size_conf.divide((
            (1, 1),
        ), spacing=0, internal=True)
        self.status_bar_var = tk.StringVar()
        self.status_bar_var.set("欢迎！")
        self.status_bar = tk.Label(
            self, relief=tk.SUNKEN, anchor=tk.W,
            textvariable=self.status_bar_var
        )

    def place_item(self):
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


if __name__ == '__main__':
    main = Main()
    main.run()
