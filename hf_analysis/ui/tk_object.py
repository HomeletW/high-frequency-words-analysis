from __future__ import annotations

import json
import logging
import threading
import time
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from datetime import datetime
from os import environ, makedirs
from os.path import abspath, basename, exists, expanduser, isdir, join, split
from typing import List, Tuple

import hf_analysis.processing.preprocess as preprocess
from hf_analysis.parameter import *
from hf_analysis.processing import prepare_data
from hf_analysis.processing.prepare_data import load_words
from hf_analysis.word import word_analysis, word_statistics


def get_home_directory():
    if DEVICE_OS in ["Linux", "Darwin"]:
        home_dir = join(expanduser("~"), "Desktop")
    elif DEVICE_OS in ["Windows"]:
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

    def place_items(self):
        raise NotImplementedError

    def set(self, *args, **kwargs):
        raise NotImplementedError

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def config(self, *args, **kwargs):
        raise NotImplementedError

    def get_size(self):
        return self.size_conf.total_size()


class SelectionDialog(tk.Toplevel):
    def __init__(self, master, title, default_value, editable=True):
        self.size_config = TopDownSizeConfig(width=400, height=500)
        width, height = self.size_config.total_size()
        super().__init__(master=master, width=width, height=height)
        self.editable = editable
        self.transient(master)
        self.title(title)
        self.resizable(0, 0)
        self.main_frame = None
        self.add_button = None
        self.minus_button = None
        self.table = None
        self.scrollbar = None
        self.import_button = None
        self.save_button = None
        self.cancel_button = None
        self.default_value = default_value
        self.prev_dir = DEFAULT_DIR
        self.values = [i for i in default_value]
        self.add_items()
        self.place_items()
        self.sync_table()
        self.grab_set()
        self.initial_focus = self.main_frame
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        # self.geometry("+%d+%d" % (master.winfo_rootx() + 50,
        #                           master.winfo_rooty() + 50))

    def start(self):
        if not self.initial_focus:
            self.initial_focus = self
        self.initial_focus.focus_set()
        self.update()
        self.deiconify()
        self.wait_window(self)

    def add_items(self):
        self.size_config.divide((
            (1, 1, 1, 1),
            (13, 19, 1),
            (1, 1, 1),
        ), spacing=DEFAULT_SPACING, internal=False)
        self.main_frame = tk.Frame(master=self)
        self.add_button = tk.Button(
            master=self.main_frame, text="添加", command=self.add)
        self.minus_button = tk.Button(
            master=self.main_frame, text="删除", command=self.minus)
        self.import_button = tk.Button(
            master=self.main_frame, text="导入", command=self.import_)
        self.save_button = tk.Button(
            master=self.main_frame, text="确认", command=self.save)
        self.cancel_button = tk.Button(
            master=self.main_frame, text="取消", command=self.cancel)
        # config the scrollable frame
        self.scrollbar = tk.Scrollbar(master=self)
        self.table = tk.Listbox(
            master=self.main_frame,
            selectmode=tk.EXTENDED,
            yscrollcommand=self.scrollbar.set
        )
        self.scrollbar.config(command=self.table.yview)

        # bind some keystroke for easy operation
        self.bind("<plus>", self.add)
        self.bind("<BackSpace>", self.minus)
        self.bind("<i>", self.import_)
        self.bind("<Return>", self.save)
        self.bind("<Escape>", self.cancel)
        self.table.bind("<Double-Button-1>", self.edit)
        if not self.editable:
            self.add_button.config(state=tk.DISABLED)
            self.minus_button.config(state=tk.DISABLED)
            self.import_button.config(state=tk.DISABLED)

    def place_items(self):
        width, height = self.size_config.total_size()
        self.main_frame.place(x=0, y=0, width=width, height=height)
        self.size_config.place([
            [self.add_button, self.minus_button, self.import_button],
            [self.table, self.scrollbar],
            [self.save_button, self.cancel_button]
        ])

    def sync_table(self):
        self.table.delete(0, tk.END)
        for v in self.values:
            self.table.insert(tk.END, v)

    def sync_values(self):
        self.values = self.table.get(0, tk.END)[::]

    def edit(self, _=None):
        if not self.editable:
            return
        selected = self.table.curselection()
        if len(selected) != 1:
            return
        s = simpledialog.askstring(parent=self, title="更改", prompt="请输入新的词汇",
                                   initialvalue=self.table.get(selected[0]))
        if not s:
            return
        self.table.delete(selected[0])
        self.table.insert(selected[0], s)
        self.sync_values()

    def add(self, _=None):
        if not self.editable:
            return
        s = simpledialog.askstring(parent=self, title="添加一个词汇", prompt="请输入词汇")
        if not s:
            return
        self.values.append(s)
        self.sync_table()
        self.table.see(tk.END)

    def minus(self, _=None):
        if not self.editable:
            return
        selected = self.table.curselection()
        if len(selected) == 0:
            return
        # ask the user to delete them or not
        ret = messagebox.askyesnocancel(
            parent=self, title="确认删除么？",
            message="您确认把选择的词汇删除么？")
        if ret is None or not ret:
            return
        all_items = self.table.get(0, tk.END)
        self.values = [all_items[index] for index in range(len(all_items))
                       if index not in selected]
        self.sync_table()

    def import_(self, _=None):
        if not self.editable:
            return
        p = ask_open_file(
            master=self, title="导入",
            filetypes=(FILE_TYPE_TXT, FILE_TYPE_WORD, FILE_TYPE_EXCEL),
            initdir=self.prev_dir)
        if not p:
            return
        if len(self.values) != 0:
            # ask the user to delete them or not
            ret = messagebox.askyesnocancel(
                parent=self, title="追加还是覆盖？",
                message="是否将导入的词汇\n"
                        "追加到当前词汇 (yes)\n"
                        "还是覆盖当前词汇 (no)?"
            )
            if ret is None:
                return
        else:
            ret = False
        words = load_words(p)
        if ret:
            self.values = self.values + words
        else:
            self.values = words
        self.sync_table()

    def cancel(self, _=None):
        self.values = self.default_value
        self.master.focus_set()
        self.destroy()

    def save(self, _=None):
        self.sync_values()
        self.master.focus_set()
        self.destroy()

    def get(self):
        return self.values

    def set(self, value):
        self.values = value
        self.sync_table()


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


class EditFieldPair(InfoPair):
    def __init__(self, master, name, size_conf):
        super().__init__(master, size_conf)
        self.name = name
        self.button = None
        self.text_field = None
        self.dialog = None
        self.values = []
        self.lock = threading.Lock()
        self.add_items()
        self.place_items()

    def add_items(self):
        self.size_conf.divide((
            (1, 1),
            (5, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.button = tk.Button(master=self, text="编辑 {}".format(self.name),
                                command=self._on_press)
        self.text_field = tk.Text(
            master=self, state=tk.DISABLED
        )

    def _on_press(self):
        if self.dialog is None:
            self.dialog = SelectionDialog(master=self,
                                          title="编辑 {}".format(self.name),
                                          default_value=self.values)
            with self.lock:
                self.dialog.start()
                self.set(self.dialog.get())
            self.dialog = None

    def place_items(self):
        self.size_conf.place([
            [self.button],
            [self.text_field],
        ])

    def config(self, *args, **kwargs):
        self.button.config(*args, **kwargs)
        state = kwargs["state"]
        if state == tk.DISABLED:
            # we need to close the window if exist
            if self.dialog is not None:
                messagebox.showinfo(
                    parent=self.dialog,
                    title="正在关闭对话框",
                    message="对话框正在被关闭以保证其他进程的正确运行!\n"
                            "您的改变将会被记录！")
                self.dialog.save()

    def set(self, value):
        self.values = value
        self.text_field.config(state=tk.NORMAL)
        self.text_field.delete(1.0, tk.END)
        self.text_field.insert(tk.END, ",\n".join(value))
        self.text_field.config(state=tk.DISABLED)

    def get(self):
        return list(self.values)


class CheckButtonPair(InfoPair):
    def __init__(self, master, text, size_conf, anchor=tk.CENTER, value_on=True,
                 value_off=False):
        super().__init__(master, size_conf)
        self.var = tk.BooleanVar()
        self.checkbutton = None
        self.add_items(text, value_on, value_off, anchor)
        self.place_items()

    def add_items(self, text, value_on, value_off, anchor):
        self.size_conf.divide((
            (1, 1),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.checkbutton = tk.Checkbutton(
            master=self, text=text, onvalue=value_on, offvalue=value_off,
            anchor=anchor, variable=self.var
        )

    def place_items(self):
        self.size_conf.place([
            [self.checkbutton],
        ])

    def config(self, *args, **kwargs):
        self.checkbutton.config(*args, **kwargs)

    def set(self, value):
        self.var.set(value)

    def get(self):
        return self.var.get()


class LabelScalePair(InfoPair):
    def __init__(self, master, label_text, from_, to_, size_conf):
        super().__init__(master, size_conf)
        self.text_var = tk.StringVar()
        self.scale_var = tk.IntVar()
        self.label = None
        self.scale = None
        self.scale_indicator = None
        self.add_items(label_text, from_, to_)
        self.place_items()

    def add_items(self, label_text, from_, to_):
        self.size_conf.divide((
            (1, 1),
            (3, 1, 4),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.label = tk.Label(master=self, text=label_text, anchor=tk.CENTER)
        self.scale_indicator = tk.Label(master=self, textvariable=self.text_var)
        self.scale = tk.Scale(master=self, from_=from_, to=to_,
                              orient=tk.HORIZONTAL, repeatinterval=200,
                              command=self._update_text,
                              variable=self.scale_var, showvalue=True)

    def place_items(self):
        self.size_conf.place([
            [self.label],
            [self.scale_indicator, self.scale],
        ])

    def config(self, *args, **kwargs):
        self.label.config(*args, **kwargs)
        self.scale_indicator.config(*args, **kwargs)
        self.scale.config(*args, **kwargs)

    def _update_text(self, _):
        val = self.get()
        if val <= 0:
            self.text_var.set("全部")
        else:
            self.text_var.set(str(val))

    def set(self, value):
        self.scale.set(value)
        self._update_text(value)

    def get(self):
        return self.scale.get()


class RadioButtonPair(InfoPair):
    """
    [ label ]
    [ buttons ... ]
    """

    def __init__(self, master, label_text, options, var, size_conf):
        """
        variables : [ ("text", "value"), ... ]
        """
        super().__init__(master, size_conf)
        self.var = var()
        self.label = None
        self.options = options
        self.buttons = []
        self.add_items(label_text)
        self.place_items()

    def add_items(self, label_text):
        self.size_conf.divide((
            (1, 1),
            (2,) + tuple(1 for _ in range(len(self.options))),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.label = tk.Label(master=self, text=label_text)
        for text, value in self.options:
            b = tk.Radiobutton(master=self, text=text,
                               variable=self.var, value=value)
            self.buttons.append(b)

    def place_items(self):
        self.size_conf.place([
            [self.label],
            self.buttons
        ])

    def config(self, *args, **kwargs):
        self.label.config(*args, **kwargs)
        for b in self.buttons:
            b.config(*args, **kwargs)

    def set(self, value):
        self.var.set(value)

    def get(self):
        return self.var.get()


class ButtonLabelPair(InfoPair):
    """[ Button, Label ]"""

    def __init__(self, master, button_text, button_func, size_conf,
                 mandatory_field=True):
        super().__init__(master, size_conf)
        self.button = None
        self.label = None
        self.text_var = None
        self._text_value = ""
        self.mandatory_field = mandatory_field
        self.add_items(button_text, button_func)
        self.place_items()

    def add_items(self, button_text, button_func):
        self.size_conf.divide((
            (1, 2, 3),
        ), spacing=DEFAULT_SPACING, internal=True)
        self.button = tk.Button(master=self, text=button_text,
                                command=button_func, anchor=tk.W)
        self.text_var = tk.StringVar()
        self.label = tk.Label(master=self, textvariable=self.text_var,
                              anchor=tk.W)
        self.label.bind("<Button-3>", self.label_del_info)
        self.label.bind("<Button-1>", self.label_show_info)

    def place_items(self):
        self.size_conf.place([
            [self.button, self.label]
        ])

    def config(self, *args, **kwargs):
        self.button.config(*args, **kwargs)
        self.label.config(*args, **kwargs)

    def set(self, value):
        path_name, file_name = split(value)
        folder_name = basename(path_name)
        self.text_var.set(join(folder_name, file_name))
        self._text_value = value
        self.sync_status()

    def get(self):
        return self._text_value

    def sync_status(self):
        if self.mandatory_field:
            info = self.get()
            if info == "-" or info == "" or not exists(info):
                self.set_button_fg("red")
            else:
                self.set_button_fg("black")
        else:
            self.set_button_fg("black")

    def set_button_fg(self, color):
        self.button.config(fg=color)

    def label_show_info(self, _):
        message = self.get()
        if message != "" and message != "-":
            message = "目录为：\n" + message
        else:
            message = "未选择目录"
        tk.messagebox.showinfo(parent=self, title="详情",
                               message=message)

    def label_del_info(self, _):
        message = self.get()
        if message != "" and message != "-":
            ret = tk.messagebox.askyesnocancel(
                parent=self, title="确认清除",
                message="确定清除现有路径么？\n"
                        "\n"
                        "现有路径为 : {}".format(message)
            )
            if ret is None or not ret:
                return
            self.set("")


class LabelEntryPair(InfoPair):
    """[ Label, entry, <button> ]"""

    def __init__(self, master, label_text, size_conf, button_text=None,
                 button_func=None):
        super().__init__(master, size_conf)
        self.label = None
        self.entry = None
        self.button = None
        self.add_items(label_text, button_text, button_func)
        self.place_items()

    def add_items(self, label_text, button_text,
                  button_func):
        self.label = tk.Label(master=self, text=label_text, anchor=tk.W)
        self.entry = tk.Entry(master=self, bd=2)
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

    def place_items(self):
        if self.button is not None:
            self.size_conf.place([[self.label, self.entry, self.button]])
        else:
            self.size_conf.place([[self.label, self.entry]])

    def config(self, *args, **kwargs):
        self.label.config(*args, **kwargs)
        self.entry.config(*args, **kwargs)
        if self.button is not None:
            self.button.config(*args, **kwargs)

    def set(self, value):
        set_entry_value(self.entry, value)

    def get(self):
        return self.entry.get()


def set_entry_value(entry_target, value):
    entry_target.delete(0, tk.END)
    entry_target.insert(0, value)


FILE_TYPE_ALL_FILE = ("所有文件", "*.*")
FILE_TYPE_EXCEL = ("Excel 文件", ".xlsx .xls")
FILE_TYPE_WORD = ("Word 文件", ".docx .doc")
FILE_TYPE_TXT = ("TXT 文件", ".txt")
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


class ProgressTracker:
    def __init__(self,
                 enable_print_out: bool = True,
                 update_func=None) -> None:
        self._enable_print_out = enable_print_out
        self._update_func = update_func
        # message
        if not exists(LOG_PATH):
            makedirs(LOG_PATH)
        time_stamp = self._time_stamp()
        name = "{}_{}.log".format(time_stamp.date(), time_stamp.time())
        logging.basicConfig(
            filename=join(LOG_PATH, name),
            filemode="w+",
            style="{",
            format="{threadName:<20s} <{levelname:<7s}> "
                   "[{asctime:<15s}] {message}"
        )
        self._logger = logging.getLogger("Main Logger")
        self._logger.setLevel(logging.DEBUG)
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
            self._start_time = time.time()
            self._end_time = None
            self._update(mode=TRACKER_TICK_INIT,
                         process_name=self._process_name,
                         process_disc=self._process_disc,
                         total_tick=self._total_tick,
                         init_tick=self._init_tick,
                         start=True)
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

    def tick(self, amount: int = 1, disc_fill: str = None) -> None:
        if amount <= 0:
            return
        prev = self._current_tick
        pending_amount = prev + amount
        if pending_amount < self._total_tick:
            self._current_tick = pending_amount
            end = False
        else:
            self._current_tick = self._total_tick
            end = True
        if end:
            self._end_time = time.time()
        time_remain = self.predict_time_remaining()
        self._update(mode=TRACKER_TICK,
                     time_remain=time_remain,
                     process_disc=self._process_disc,
                     total_tick=self._total_tick,
                     current_tick=self._current_tick,
                     amount=self._current_tick - prev,
                     disc_fill=disc_fill,
                     end=end)

    def tick_parent(self, amount: int = 1) -> None:
        if amount <= 0:
            return
        self._parent_current_tick += amount
        self._update(mode=TRACKER_PARENT_TICK,
                     current_tick=self._parent_current_tick)

    def log(self, message: str, tp=TRACKER_LOG_INFO,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            extra=None,
            prt=False) -> None:
        if prt:
            print(message)
        message = message.strip()
        self._logger.log(
            level=tp,
            msg=message, exc_info=exc_info, stack_info=stack_info,
            stacklevel=stacklevel, extra=extra
        )
        # self._message.append((self._time_stamp(), tp, message))
        self._update(mode=TRACKER_LOG, tp=tp, prt=prt, message=message)

    def get_logger(self):
        return self._logger

    def time_elapsed(self, use_time_accum=False) -> str:
        if not use_time_accum:
            if self._start_time is None or self._end_time is None:
                return ""
            time_elapsed = self._end_time - self._start_time
        else:
            time_elapsed = self._time_accum
        return self._format_time(time_elapsed)

    @staticmethod
    def _time_stamp():
        return datetime.fromtimestamp(time.time())

    @staticmethod
    def _format_time(time_):
        hours, rem = divmod(time_, 3600)
        minutes, second = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes),
                                             int(second))

    def predict_time_remaining(self):
        if self._start_time is None:
            return ""
        time_elapsed = time.time() - self._start_time
        average_time_use_per_tick = time_elapsed / (
                self._current_tick - self._init_tick)
        time_remaining = average_time_use_per_tick * (
                self._total_tick - self._current_tick)
        return self._format_time(round(time_remaining))

    def _update(self, **kwargs):
        if kwargs["mode"] == TRACKER_TICK:
            amount = kwargs["amount"]
            end = kwargs["end"]
            if self._enable_print_out:
                # if this is the first time printing, we also print the header
                print("=" * amount, end="")
                if end:
                    time_elapsed = self.time_elapsed()
                    print("| Time Elapsed : {}".format(time_elapsed))
                    # also log itself
                    self.log(
                        "{} 结束！ 用时 : {} [desc={}, init={}, total={}]".format(
                            self._process_name,
                            time_elapsed,
                            self._process_disc,
                            self._init_tick,
                            self._total_tick,
                        ))
                    self._time_accum += self._end_time - self._start_time
        elif kwargs["mode"] == TRACKER_TICK_INIT:
            start = kwargs["start"]
            if start:
                print("{0:s} {1:>5d}|".format(self._process_name,
                                              self._total_tick), end="")
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


class ThreadWrapper:
    def __init__(self,
                 name,
                 master,
                 tracker,
                 thread_type,
                 info_handler,
                 start_process=None,
                 end_process=None):
        self._name = name
        self._thread = None
        self._thread_type = thread_type
        self._master = master
        self._tracker = tracker
        self._start_process = start_process
        self._end_process = end_process
        self._info_handler = info_handler
        self._lock = threading.Lock()

    def _starting_process(self):
        if self._start_process is not None:
            self._start_process()

    def _ending_process(self):
        if self._end_process is not None:
            self._end_process()

    def _check_process(self):
        if self._thread is not None:
            if self._thread.is_finished():
                # check the error log
                error = self._thread.get_error()
                self._thread.join()
                self._ending_process()
                self._thread = None
                # notify the user about the error
                if error is not None:
                    info, type_ = error
                    if type_ in [THREAD_VALUE_ERROR]:
                        tk.messagebox.showerror(
                            parent=self._master,
                            title="{} 错误".format(self._name),
                            message="{}进程以 值错误 结束！\n"
                                    "请检查值对应域是否填写正确！\n"
                                    "前往 https://github.com/HomeletW/high-"
                                    "frequency-words-analysis 查看该错误的解决办法!\n"
                                    "\n"
                                    "错误信息:\n".format(self._name) + info
                        )
                    elif type_ in [THREAD_OTHER_ERROR]:
                        tk.messagebox.showerror(
                            parent=self._master,
                            title="{} 错误".format(self._name),
                            message="{}进程以 意外错误 结束！\n"
                                    "请联系开发人员并汇报该错误！\n"
                                    "或者前往 https://github.com/HomeletW/high-"
                                    "frequency-words-analysis 查看该错误的解决办法!\n"
                                    "\n"
                                    "错误信息:\n".format(self._name) + info
                        )
            else:
                self._master.after(100, self._check_process)

    def run(self, ask=True):

        if self._thread is None:
            # if no such process is running,
            # we ask user if we can create one
            if ask:
                ret = tk.messagebox.askyesnocancel(
                    parent=self._master,
                    title="确认",
                    message="您确定要进行 {} 么？\n"
                            "这可能需要很长时间, 且一旦开始不可停止.".format(self._name)
                )
                if ret is None or not ret:
                    return
            self._starting_process()
            with self._lock:
                self._thread = self._thread_type(self._tracker,
                                                 self._info_handler)
            self._thread.start()
            self._master.after(100, self._check_process)
        else:
            # if there is something running, we let user wait
            tk.messagebox.showwarning(
                parent=self._master,
                title="请稍候",
                message="{}中，请稍候...".format(self._name)
            )

    def get_thread(self):
        return self._thread


class InfoHandler:
    def __init__(self):
        self._value_handler = {}
        self._arg_handler = {}

    def register_field(self, source, key, default,
                       not_none=False, not_empty=False, not_=None, type_=None):
        self._arg_handler[key] = (
            source, default, not_none, not_empty, not_, type_)
        self._value_handler[key] = default

    def _check_exist(self, key):
        if key not in self._arg_handler or key not in self._value_handler:
            raise KeyError("Key not registered! [key='{}']".format(
                INFO_FIELD_NAME.get(key, key)))

    def _check_valid(self, key, value):
        _, _, not_none, not_empty, not_, type_ = \
            self._arg_handler[key]
        if not_none and value is None:
            raise ValueError(
                "域 {} 不应为 None".format(INFO_FIELD_NAME.get(key, key)))
        elif type_ is not None and not isinstance(value, type_):
            raise ValueError(
                "域 {} 类型应为 {}, 不应为 {}".format(
                    INFO_FIELD_NAME.get(key, key), type_, type(value)))
        elif not_empty and len(value) == 0:
            raise ValueError(
                "域 {} 不应为空".format(INFO_FIELD_NAME.get(key, key)))
        elif not_ is not None and value == not_:
            raise ValueError(
                "域 {} 不应为 {}".format(INFO_FIELD_NAME.get(key, key), not_))
        return value

    def put_field(self, key, value):
        self._check_exist(key)
        self._value_handler[key] = value

    def fetch_field(self, key, check=True):
        self._check_exist(key)
        source = self._arg_handler[key][0]
        if source is None:
            value = self._value_handler[key]
        else:
            value = source.get()
        if check:
            value = self._check_valid(key, value)
        self._value_handler[key] = value

    def fetch_all(self, check=True):
        for key in self._value_handler:
            self.fetch_field(key, check=check)

    def get(self, key, fetch=True):
        if fetch:
            self.fetch_field(key)
        else:
            self._check_exist(key)
        return self._value_handler[key]

    def freeze(self, key):
        self._check_exist(key)
        source = self._arg_handler[key][0]
        if source is not None:
            source.config(state=tk.DISABLED)

    def unfreeze(self, key):
        self._check_exist(key)
        source = self._arg_handler[key][0]
        if source is not None:
            source.config(state=tk.NORMAL)

    def freeeze(self, keys):
        for key in keys:
            self.freeze(key)

    def unfreeeze(self, keys):
        for key in keys:
            self.unfreeze(key)

    def is_available(self, key):
        try:
            self.get(key)
            return True
        except ValueError:
            return False

    def sync_field(self, key):
        self._check_exist(key)
        source = self._arg_handler[key][0]
        if source is None:
            return
        value = self.get(key, fetch=False)
        source.set(value)

    def sync_all(self):
        for key in self._value_handler:
            self.sync_field(key)

    def report(self, *args, **kwargs) -> Tuple[tuple, dict]:
        arg_rep = tuple(self.get(key, fetch=True) for key in args)
        kwarg_rep = {key: self.get(value, fetch=True) for key, value in
                     kwargs.items()}
        return arg_rep, kwarg_rep

    def write_to_json(self, tracker, exclude=()):
        path = abspath(JSON_PATH)
        try:
            self.fetch_all(check=False)
            value = {key: value for key, value in self._value_handler.items() if
                     key not in exclude}
            with open(path, "w+") as js:
                json.dump(value, js, indent=4)
        except Exception as e:
            tracker.log("Fail to write JSON ({})".format(path),
                        tp=TRACKER_LOG_ERROR, exc_info=e, prt=True)
            return
        tracker.log("Saved JSON to {}".format(path),
                    tp=TRACKER_LOG_INFO, prt=True)

    def load_from_json(self, tracker):
        path = abspath(JSON_PATH)
        try:
            with open(path, "r") as js:
                value = json.load(js)
            for key, v in value.items():
                if key in self._value_handler:
                    self._value_handler[key] = v
                else:
                    tracker.log(
                        "Skipping {}, since it is not registered!".format(key),
                        tp=TRACKER_LOG_INFO, prt=True)
        except Exception as e:
            tracker.log("Fail to load JSON ({}), using default.".format(path),
                        tp=TRACKER_LOG_ERROR, exc_info=e, prt=True)
            return
        tracker.log("Loaded from JSON ({})".format(path),
                    tp=TRACKER_LOG_INFO, prt=True)


class PreprocessThread(threading.Thread):
    def __init__(self, tracker, info_handler):
        super().__init__(name="Preprocess Thread", daemon=True)
        self._info_handler = info_handler
        self._tracker = tracker
        self._finished = False
        self._error = None

    def run(self):
        self._tracker.log("启动预处理线程!")
        vars_ = [
            INFO_PATH_ROOT,
            INFO_PATH_INDEX,
            INFO_PATH_ADDITIONAL_PARM,
            INFO_PDF_ENGINE,
            INFO_PDF_FORMAT,
            INFO_PDF_DPI,
            INFO_OCR_DEF_LANG,
        ]
        try:
            self._info_handler.freeeze(vars_)
            # fetch all the variable
            output_folder = self._info_handler.get(INFO_PATH_ROOT)
            path_to_index = self._info_handler.get(INFO_PATH_INDEX)
            path_to_additional_parm = self._info_handler.get(
                INFO_PATH_ADDITIONAL_PARM)
            engine = self._info_handler.get(INFO_PDF_ENGINE)
            cov_format = self._info_handler.get(INFO_PDF_FORMAT)
            dpi = self._info_handler.get(INFO_PDF_DPI)
            default_lang = self._info_handler.get(INFO_OCR_DEF_LANG)
            preprocess.process(
                path_to_index=path_to_index,
                path_to_additional_parm=path_to_additional_parm,
                output_folder=output_folder,
                dpi=dpi,
                cov_format=cov_format,
                engine=engine,
                default_lang=default_lang,
                tracker=self._tracker,
            )
        except ValueError as v:
            message = str(v)
            self._error = (message, THREAD_VALUE_ERROR)
            self._tracker.log("预处理线程由于 参数错误 终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=v)
        except Exception as e:
            message = str(e)
            self._error = (message, THREAD_OTHER_ERROR)
            self._tracker.log("预处理线程意外终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=e)
        finally:
            if not self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                total_time = self._tracker.time_elapsed(use_time_accum=True)
                self._tracker.clear_time_accum()
                self._tracker.log("处理完成！ 用时 : {}".format(total_time),
                                  prt=True)
            self._tracker.reset_ticker()
            self._tracker.reset_parent()
            self._tracker.log("结束预处理线程!")
            self._info_handler.unfreeeze(vars_)
            self._finished = True

    def is_finished(self):
        return self._finished

    def get_error(self):
        return self._error

    def is_successful(self):
        return self._error is None


class LoadDataThread(threading.Thread):
    def __init__(self, tracker, info_handler):
        super().__init__(name="Load Data Thread", daemon=True)
        self._info_handler = info_handler
        self._tracker = tracker
        self._finished = False
        self._return_value = None
        self._error = None

    def run(self):
        self._tracker.log("启动装载数据线程!")
        vars_ = [
            INFO_PATH_ROOT
        ]
        try:
            self._info_handler.freeeze(vars_)
            root_path = self._info_handler.get(INFO_PATH_ROOT)
            self._return_value = prepare_data.prepare_data(
                root_path=root_path,
                tracker=self._tracker
            )
        except ValueError as v:
            message = str(v)
            self._error = (message, THREAD_VALUE_ERROR)
            self._tracker.log("装载数据线程由于 参数错误 终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=v)
        except Exception as e:
            message = str(e)
            self._error = (message, THREAD_OTHER_ERROR)
            self._tracker.log("装载数据线程意外终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=e)
        finally:
            if not self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                total_time = self._tracker.time_elapsed(use_time_accum=True)
                self._tracker.clear_time_accum()
                self._tracker.log("处理完成！ 用时 : {}".format(total_time),
                                  prt=True)
            self._tracker.reset_ticker()
            self._tracker.reset_parent()
            self._tracker.log("结束装载数据线程!")
            self._info_handler.unfreeeze(vars_)
            self._finished = True

    def is_finished(self):
        return self._finished

    def get_error(self):
        return self._error

    def get_return_value(self):
        return self._return_value

    def is_successful(self):
        return self._error is None


class ExtractionThread(threading.Thread):
    def __init__(self, tracker, info_handler):
        super().__init__(name="Extraction Thread", daemon=True)
        self._info_handler = info_handler
        self._tracker = tracker
        self._finished = False
        self._return_value = None
        self._error = None

    def run(self):
        self._tracker.log("启动抽取词汇线程!")
        vars_ = [
            INFO_LOADER_RAW_DATA,
            INFO_ANALYZE_NUM_WANTED,
            INFO_ANALYZE_EXTRACTOR,
            INFO_ANALYZE_SUGGESTION_WORD,
            INFO_ANALYZE_WHITELIST_WORD,
            INFO_ANALYZE_BLACKLIST_WORD,
        ]
        try:
            self._info_handler.freeeze(vars_)
            data = self._info_handler.get(INFO_LOADER_RAW_DATA)
            num_wanted = self._info_handler.get(INFO_ANALYZE_NUM_WANTED)
            extractor = self._info_handler.get(INFO_ANALYZE_EXTRACTOR)
            suggestion_word = self._info_handler.get(
                INFO_ANALYZE_SUGGESTION_WORD)
            whitelist_word = self._info_handler.get(INFO_ANALYZE_WHITELIST_WORD)
            blacklist_word = self._info_handler.get(INFO_ANALYZE_BLACKLIST_WORD)
            self._return_value = word_analysis.summarise(
                data=data,
                suggestion_word=suggestion_word,
                whitelist_word=whitelist_word,
                blacklist_word=blacklist_word,
                num_wanted=num_wanted,
                extractor=extractor,
                tracker=self._tracker,
            )
        except ValueError as v:
            message = str(v)
            self._error = (message, THREAD_VALUE_ERROR)
            self._tracker.log("抽取词汇线程由于 参数错误 终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=v)
        except Exception as e:
            message = str(e)
            self._error = (message, THREAD_OTHER_ERROR)
            self._tracker.log("抽取词汇线程意外终止！ [error='{}']".format(str(e)),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=e)
        finally:
            if not self._info_handler.get(INFO_ACTION_AUTO_NEXT_STEP):
                total_time = self._tracker.time_elapsed(use_time_accum=True)
                self._tracker.clear_time_accum()
                self._tracker.log("处理完成！ 用时 : {}".format(total_time),
                                  prt=True)
            self._tracker.reset_ticker()
            self._tracker.reset_parent()
            self._tracker.log("结束抽取词汇线程!")
            self._info_handler.unfreeeze(vars_)
            self._finished = True

    def is_finished(self):
        return self._finished

    def get_error(self):
        return self._error

    def get_return_value(self):
        return self._return_value

    def is_successful(self):
        return self._error is None


class AnalyzeThread(threading.Thread):
    def __init__(self, tracker, info_handler):
        super().__init__(name="Analyze Thread", daemon=True)
        self._info_handler = info_handler
        self._tracker = tracker
        self._finished = False
        self._return_value = None
        self._error = None

    def run(self):
        self._tracker.log("启动统计分析线程!")
        vars_ = [
            INFO_EXTRACTOR_SEGMENTS,
            INFO_ANALYZE_STAT_ANALYZER
        ]
        try:
            self._info_handler.freeeze(vars_)
            segment = self._info_handler.get(INFO_EXTRACTOR_SEGMENTS)
            statistics_analyzer = self._info_handler.get(
                INFO_ANALYZE_STAT_ANALYZER)
            self._return_value = word_statistics.analyze(
                segment=segment,
                tracker=self._tracker,
                statistics_analyzer=statistics_analyzer
            )
        except ValueError as v:
            message = str(v)
            self._error = (message, THREAD_VALUE_ERROR)
            self._tracker.log("统计分析线程由于 参数错误 终止！ [error='{}']".format(message),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=v)
        except Exception as e:
            message = str(e)
            self._error = (message, THREAD_OTHER_ERROR)
            self._tracker.log("统计分析线程意外终止！ [error='{}']".format(str(e)),
                              tp=TRACKER_LOG_ERROR, prt=True, exc_info=e)
        finally:
            total_time = self._tracker.time_elapsed(use_time_accum=True)
            self._tracker.clear_time_accum()
            self._tracker.log("处理完成！ 用时 : {}".format(total_time), prt=True)
            self._tracker.reset_ticker()
            self._tracker.reset_parent()
            self._tracker.log("结束统计分析线程!")
            self._info_handler.unfreeeze(vars_)
            self._finished = True

    def is_finished(self):
        return self._finished

    def get_error(self):
        return self._error

    def get_return_value(self):
        return self._return_value

    def is_successful(self):
        return self._error is None


if __name__ == '__main__':

    def test(event):
        print('keysym:', event.keysym)


    root = tk.Tk()

    root.bind('<Key>', test)

    root.mainloop()
