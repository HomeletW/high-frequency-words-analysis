# -*- coding: utf-8 -*-

import tkinter
import tkinter.messagebox as messagebox

from hf_analysis.parameter import INFO_PATCH
from hf_analysis.ui.UI import MainApplication
from hf_analysis.ui.tk_object import InfoHandler, TRACKER_LOG_ERROR

PATCH = "V 0.1"


def main():
    info_handler = InfoHandler()
    tk = tkinter.Tk()
    info_handler.register_field(
        None, INFO_PATCH, "",
    )
    info_handler.put_field(INFO_PATCH, PATCH)
    application = MainApplication(tk, info_handler)
    tracker = application.get_tracker()
    try:
        application.run()
    except Exception as e:
        s = str(e)
        tracker.log("未知错误！ [error='{}']".format(s),
                    tp=TRACKER_LOG_ERROR, exc_info=e, prt=True)
        messagebox.showerror(title="程序错误",
                             message="出现未知的程序错误！\n"
                                     "请联系开发者并汇报该错误！\n"
                                     "\n"
                                     "错误信息:\n{}".format(s))


if __name__ == '__main__':
    main()
