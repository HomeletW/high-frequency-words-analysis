from __future__ import annotations

import platform
import threading
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from os import environ
from os.path import expanduser, isdir, join
from typing import List, Tuple

import hf_analysis.processing.preprocess as preprocess


def get_home_directory():
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        home_dir = join(expanduser("~"), "Desktop")

    elif system in ["Windows"]:
        home_dir = join(environ["USERPROFILE"], "Desktop")
    else:
        home_dir = None
    if home_dir is not None and isdir(home_dir):
        return home_dir
    else:
        return "/"


DEFAULT_HEIGHT = 30
DEFAULT_WIDTH = 200
DEFAULT_SPACING = 5


class Sizeable:
    def get_size(self):
        raise NotImplementedError


class InfoPair(tk.Frame, Sizeable):
    def __init__(self, master, size_conf):
        width, height = size_conf.total_size()
        super().__init__(master, width=width, height=height)
        self.size_conf = size_conf

    def add_items(self, *args, **kwargs):
        raise NotImplementedError

    def place_item(self):
        raise NotImplementedError

    def set_info(self, *args, **kwargs):
        raise NotImplementedError

    def get_info(self, *args, **kwargs):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()


class TwoStageButton(tk.Button):
    def __init__(self, master, command, text_choice, init_pos: bool):
        self.button_text_var = tk.StringVar()
        super().__init__(master=master, command=command,
                         textvariable=self.button_text_var)
        self.text_choice = text_choice
        self.button_text_var.set(self.text_choice[init_pos])
        self.pos = init_pos
        self._sync_fg()

    def flip(self):
        self.pos = not self.pos
        self.button_text_var.set(self.text_choice[self.pos])
        # apply a foreground color change
        self._sync_fg()

    def _sync_fg(self):
        if self.pos:
            self.config(fg="black")
        else:
            self.config(fg="red")


class RadioButtonPair(InfoPair):
    """
    [ label ]
    [ buttons ... ]
    """

    def __init__(self, master, label_text, variables,
                 size_conf: SimpleSizeConfig, default_value: int = 0):
        """
        variables : [ ("text", "value"), ... ]
        """
        super().__init__(master, size_conf)
        self.text_var = None
        self.label = None
        self.variable = variables
        self.buttons = []
        self.add_items(label_text, variables, default_value)
        self.place_item()

    def add_items(self, label_text, variables, default_value):
        self.size_conf.divide((
            (1, 1),
            (2,) + tuple(1 for _ in range(len(variables))),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.label = tk.Label(master=self, text=label_text)
        self.text_var = tk.StringVar()
        self.text_var.set(variables[default_value][1])
        for text, value in variables:
            b = tk.Radiobutton(master=self, text=text,
                               variable=self.text_var, value=value)
            self.buttons.append(b)

    def place_item(self):
        self.size_conf.place([
            [self.label],
            self.buttons
        ])

    def set_info(self, value):
        self.text_var.set(value)

    def get_info(self):
        self.text_var.get()


class ButtonLabelPair(InfoPair):
    """[ Button, Label ]"""

    def __init__(self, master, button_text, button_func, label_text, size_conf):
        super().__init__(master, size_conf)
        self.button = None
        self.label = None
        self.text_var = None
        self.add_items(button_text, button_func, label_text)
        self.place_item()

    def add_items(self, button_text, button_func, label_text):
        self.size_conf.divide((
            (1, 2, 3),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.button = tk.Button(master=self, text=button_text,
                                command=button_func, anchor=tk.W)
        self.text_var = tk.StringVar()
        self.text_var.set(label_text)
        self.label = tk.Label(master=self, textvariable=self.text_var,
                              anchor=tk.W)
        self.label.bind("<Double-Button-1>", self.label_on_key_press)

    def place_item(self):
        self.size_conf.place([[self.button, self.label]])

    def set_info(self, value):
        self.text_var.set(value)

    def get_info(self):
        return self.text_var.get()

    def set_button_fg(self, color):
        self.button.config(fg=color)

    def label_on_key_press(self, event):
        message = self.get_info()
        if message != "" and message != "-":
            message = "目录为：\n" + message
            tk.messagebox.showinfo(parent=self, title="详情",
                                   message=message)


class LabelEntryPair(InfoPair):
    """[ Label, entry, <button> ]"""

    def __init__(self, master, label_text, entry_placeholder,
                 size_conf: SimpleSizeConfig,
                 button_text=None, button_func=None):
        super().__init__(master, size_conf)
        self.label = None
        self.entry = None
        self.button = None
        self.add_items(label_text, entry_placeholder, button_text, button_func)
        self.place_item()

    def add_items(self, label_text, entry_placeholder, button_text,
                  button_func):
        self.label = tk.Label(master=self, text=label_text, anchor=tk.W)
        self.entry = tk.Entry(master=self, bd=2)
        self.entry.insert(tk.END, entry_placeholder)
        if button_text is not None:
            # add the button
            self.button = tk.Button(master=self, text=button_text,
                                    command=button_func)
            self.size_conf.divide((
                (1, 2, 4, 1),
            ), spacing=DEFAULT_SPACING, internal=True)
        else:
            self.size_conf.divide((
                (1, 1, 2),
            ), spacing=DEFAULT_SPACING, internal=True)

    def place_item(self):
        if self.button is not None:
            self.size_conf.place([[self.label, self.entry, self.button]])
        else:
            self.size_conf.place([[self.label, self.entry]])

    def set_info(self, value):
        set_entry_value(self.entry, value)

    def get_info(self):
        return self.entry.get()


def set_entry_value(entry_target, value):
    entry_target.delete(0, tk.END)
    entry_target.insert(0, value)


FILE_TYPE_ALL_FILE = ("所有文件", "*.*")
FILE_TYPE_EXCEL = ("Excel 文件", ".xlsx .xls")
DEFAULT_DIR = get_home_directory()


def ask_open_file(master, title, filetypes=(), initdir=DEFAULT_DIR) -> str:
    return filedialog.askopenfilename(
        parent=master,
        initialdir=initdir,
        title=title,
        filetypes=[f for f in filetypes] + [FILE_TYPE_ALL_FILE]
    )


def ask_open_directory(master, title, initdir=DEFAULT_DIR) -> str:
    return filedialog.askdirectory(
        parent=master,
        initialdir=initdir,
        title=title,
        mustexist=True
    )


def ask_save_file(master, title, filetypes=(), initdir=DEFAULT_DIR) -> str:
    return filedialog.asksaveasfilename(
        master=master,
        initialdir=initdir,
        title=title,
        filetypes=[f for f in filetypes] + [FILE_TYPE_ALL_FILE]
    )


TRACKER_LOG = "tracker_log"
TRACKER_TICK = "tracker_tick"
TRACKER_PARENT_TICK = "tracker_parent_tick"
TRACKER_TICK_INIT = "tracker_tick_init"
TRACKER_PARENT_INIT = "tracker_parent_init"

TRACKER_LOG_ERROR = "ERROR"
TRACKER_LOG_INFO = "INFO"


class ProgressTracker:
    def __init__(self,
                 enable_print_out: bool = True,
                 update_func=None) -> None:
        self._enable_print_out = enable_print_out
        self._update_func = update_func
        # message
        self._message = []
        # parent progress
        self._parent_process_name = None
        self._parent_init_tick = None
        self._parent_total_tick = None
        self._parent_current_tick = None
        # tick
        self._process_name = None
        self._process_disc = None
        self._init_tick = None
        self._total_tick = None
        self._current_tick = None
        self._start_time = None
        self._end_time = None
        self._time_accum = 0

    def init_parent_progress(self, progress_name, init_tick, total_tick):
        if self._parent_current_tick is None or \
                self._parent_current_tick == self._parent_total_tick:
            self._parent_process_name = progress_name
            self._parent_init_tick = init_tick
            self._parent_total_tick = total_tick
            self._parent_current_tick = init_tick
            self._update(mode=TRACKER_PARENT_INIT,
                         process_name=self._parent_process_name,
                         total_tick=self._parent_total_tick,
                         init_tick=self._parent_init_tick)

    def init_ticker(self, process_name, process_disc, init_tick, total_tick):
        if self._current_tick is None or self._current_tick == self._total_tick:
            self._process_name = process_name
            self._process_disc = process_disc
            self._init_tick = init_tick
            self._total_tick = total_tick
            self._current_tick = init_tick
            self._start_time = None
            self._end_time = None
            self._update(mode=TRACKER_TICK_INIT,
                         process_name=self._process_name,
                         process_disc=self._process_disc,
                         total_tick=self._total_tick,
                         init_tick=self._init_tick)
            return True
        return False

    def reset_parent(self):
        self._parent_process_name = None
        self._parent_init_tick = None
        self._parent_total_tick = None
        self._parent_current_tick = None

    def reset_ticker(self):
        self._process_name = None
        self._process_disc = None
        self._init_tick = None
        self._total_tick = None
        self._current_tick = None
        self._start_time = None
        self._end_time = None

    def clear_time_accum(self):
        self._time_accum = 0

    def tick(self, amount: int = 1) -> None:
        if amount <= 0:
            return
        prev = self._current_tick
        start = prev == self._init_tick
        if start:
            self._start_time = time.time()
        pending_amount = self._current_tick + amount
        if pending_amount < self._total_tick:
            self._current_tick = pending_amount
            end = False
        else:
            self._current_tick = self._total_tick
            end = True
        if end:
            self._end_time = time.time()
        self._update(mode=TRACKER_TICK,
                     process_disc=self._process_disc,
                     total_tick=self._total_tick,
                     current_tick=self._current_tick,
                     amount=self._current_tick - prev,
                     start=start,
                     end=end)

    def tick_parent(self, amount: int = 1) -> None:
        if amount <= 0:
            return
        self._parent_current_tick += amount
        self._update(mode=TRACKER_PARENT_TICK,
                     current_tick=self._parent_current_tick)

    def log(self, message: str, tp=None, prt=False) -> None:
        if tp is None:
            tp = TRACKER_LOG_INFO
        if prt:
            print(message)
        message = message.strip()
        self._message.append((tp, message))
        self._update(mode=TRACKER_LOG, tp=tp, prt=prt, message=message)

    def time_elapsed(self, use_time_accum=False) -> str:
        if not use_time_accum:
            if self._start_time is None or self._end_time is None:
                return ""
            time_elapsed = self._end_time - self._start_time
        else:
            time_elapsed = self._time_accum
        hours, rem = divmod(time_elapsed, 3600)
        minutes, second = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes),
                                             int(second))

    def _update(self, **kwargs):
        if kwargs["mode"] == TRACKER_TICK:
            amount = kwargs["amount"]
            start = kwargs["start"]
            end = kwargs["end"]
            if self._enable_print_out:
                # if this is the first time printing, we also print the header
                if start:
                    print("{0:s} {1:>5d}|".format(self._process_name,
                                                  self._total_tick), end="")
                print("=" * amount, end="")
                if end:
                    print("| Time Elapsed : {}".format(self.time_elapsed()))
                    self._time_accum += self._end_time - self._start_time
        if self._update_func is not None:
            self._update_func(**kwargs)


class SizeConfig:
    def total_size(self):
        raise NotImplementedError

    def place(self, comp):
        raise NotImplementedError


class SimpleSizeConfig(SizeConfig):
    def __init__(self, size_config, spacing: int = 0, internal: bool = True):
        """
        For example for
            two row and first row with 2 element and second row with 3 element
        size_config should provide:
            size_config : (
            (height_1, width_1, width_2),
            (height_2, width_1, width_2, width_3)
        )
        """
        self._size_config = size_config
        self._spacing = spacing
        self._internal = internal
        self._total_size = self.get_total_size()

    def total_size(self):
        return self._total_size

    def get_total_size(self) -> Tuple[int, int]:
        if not self._internal:
            width = max(
                sum(row_size[1:]) + self._spacing * len(row_size)
                for row_size in self._size_config
            )
            height = sum(
                row_size[0] for row_size in self._size_config
            ) + self._spacing * (len(self._size_config) + 1)
        else:
            width = max(
                sum(row_size[1:]) + self._spacing * (len(row_size) - 2)
                for row_size in self._size_config
            )
            height = sum(
                row_size[0] for row_size in self._size_config
            ) + self._spacing * (len(self._size_config) - 1)
        return width, height

    def place(self, comp) -> None:
        """comps must be follow the structure of size_config"""
        y = self._spacing if not self._internal else 0
        for row, row_size in zip(comp, self._size_config):
            row_height = row_size[0]
            x = self._spacing if not self._internal else 0
            for c, width in zip(row, row_size[1:]):
                c.place(x=x, y=y, width=width, height=row_height)
                x += width + self._spacing
            y += row_height + self._spacing


class TopDownSizeConfig(SizeConfig):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._config = None
        self._spacing = None
        self._internal = None

    def divide(self,
               config,
               spacing,
               internal,
               width_offset=0,
               height_offset=0) -> \
            List[List[TopDownSizeConfig]]:
        """
        Config should be in the format of:
        (
            (HEIGHT_PROP, FIRST_WIDTH_PROP, SECOND_WIDTH_PROP, ...)
        )
        """
        self._config = []
        self._spacing = spacing
        self._internal = internal
        divided = []
        hei_config = [row[0] for row in config]
        divided_height = self._div_height(hei_config, spacing, internal,
                                          height_offset)
        for index, row in enumerate(config):
            height = divided_height[index]
            row_config = row[1:]
            divided_width = self._div_width(row_config, spacing, internal,
                                            width_offset)
            divided.append(
                [TopDownSizeConfig(width, height) for width in divided_width]
            )
            self._config.append(
                [height] + divided_width
            )
        return divided

    def _div_width(self, row_config, spacing, internal, offset) -> List[float]:
        avi_width = self._width - offset - (
            len(row_config) - 1 if internal else len(row_config) + 1) * spacing
        unit_width = avi_width / sum(row_config)
        return [unit_width * prop for prop in row_config]

    def _div_height(self, hei_config, spacing, internal, offset) -> List[float]:
        avi_height = self._height - offset - (
            len(hei_config) - 1 if internal else len(hei_config) + 1) * spacing
        unit_height = avi_height / sum(hei_config)
        return [unit_height * prop for prop in hei_config]

    def total_size(self):
        return self._width, self._height

    def place(self, comp):
        if self._config is None:
            # no config added, just put the component spans the width and height
            comp.place(x=0, y=0, width=self._width, height=self._height)
        else:
            y = 0 if self._internal else self._spacing
            for row, row_config in zip(comp, self._config):
                row_height = row_config[0]
                x = 0 if self._internal else self._spacing
                for c, width in zip(row, row_config[1:]):
                    if c is not None:
                        c.place(x=x, y=y, width=width, height=row_height)
                    x += width + self._spacing
                y += row_height + self._spacing


class PreprocessProcess(threading.Thread):
    def __init__(self,
                 path_to_index,
                 path_to_additional_parm,
                 output_folder,
                 dpi,
                 default_lang,
                 tracker):
        super().__init__(name="Preprocess Process", daemon=True)
        self._path_to_index = path_to_index
        self._path_to_additional_parm = path_to_additional_parm
        self._output_folder = output_folder
        self._dpi = dpi
        self._default_lang = default_lang
        self._tracker = tracker
        self._finished = False

    def run(self):
        self._tracker.log("启动预处理线程!", prt=True)
        preprocess.process(
            path_to_index=self._path_to_index,
            path_to_additional_parm=self._path_to_additional_parm,
            output_folder=self._output_folder,
            dpi=self._dpi,
            cov_format=".jpeg",
            default_lang=self._default_lang,
            tracker=self._tracker,
        )
        self._tracker.log("结束预处理线程!", prt=True)
        self._finished = True

    def is_finished(self):
        return self._finished


class AnalyzeProcess(threading.Thread):
    def is_finished(self):
        pass
