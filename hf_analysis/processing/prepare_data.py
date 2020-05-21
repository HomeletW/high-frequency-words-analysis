from os import listdir
from os.path import exists, isfile, join, splitext
from re import findall
from typing import Dict, List, Tuple

import pandas as pd
from docx2txt import process

from hf_analysis.parameter import *


def get_name_extension(path: str) -> Tuple[str, str]:
    return splitext(path)


def extract_content(path: str) -> str:
    """读取一个文件的全部信息"""
    _, extension = get_name_extension(path)
    if extension in [".docx", ".doc"]:
        return extract_docx(path)
    elif extension in [".xlsx", ".xls"]:
        return extract_excel(path)
    else:
        return extract_text(path)


def extract_text(path: str) -> str:
    with open(path, encoding="utf8") as f:
        return f.read()


def extract_docx(path: str) -> str:
    text = process(path)
    return "\n".join(text)


def extract_excel(path: str) -> str:
    df = pd.read_excel(path)
    return "\n".join(" ".join(str(i) for i in row) for row in df.iterrows())


def load_words(path: str) -> List[str]:
    """装载用户自定建议词典"""
    content = extract_content(path)
    return content.replace("\n", " ").split()


def prepare_data(root_path: str, tracker) -> \
        List[Tuple[Dict[str, str], str, int]]:
    """
    返回格式为：
        [ (content, category, display_name, order_index), ... ]
    """
    data_path = join(root_path, DATA_PATH)
    if not exists(data_path):
        raise ValueError("根目录没有 data 文件夹! 请先进行预处理，或选择其他根目录！")
    data = {}
    dirs = listdir(data_path)
    tracker.init_parent_progress("装载数据父程序", 0, len(dirs))
    for file_name in dirs:
        # get the abs path
        abs_path = join(data_path, file_name)
        # get the args
        file_args = splitext(file_name)[0].split("_")
        # the first args must be DATA_PREFIX and must have two arg
        if len(file_args) < 4 or file_args[0] != DATA_PREFIX:
            tracker.log("跳过 -{}- 因为文件名不符合规范".format(file_name), prt=True)
            continue
        elif not isfile(abs_path):
            tracker.log("跳过 -{}- 因为无此文件".format(file_name), prt=True)
            continue
        else:
            content = get_text(abs_path)
            category = file_args[2]
            name = file_args[3]
            order_index = int(file_args[1])
            tracker.log("处理 -{}- [category={}, name={}, order_index={}]".format(
                file_name, category, name, order_index), prt=True)
            tracker.init_ticker("   进程", "正在处理 : {}".format(name), 0, 1)
            if category not in data:
                data[category] = ({}, order_index)
            c_dict, o_index = data[category]
            if o_index != order_index:
                tracker.log(
                    "读取数据错误！ 相同类别, 不同排序, 自动分类成 {} : "
                    "[file={}, index={}, expected_index={}]".format(
                        o_index, abs_path, order_index, o_index
                    ),
                    tp=TRACKER_LOG_ERROR, prt=True)
            c_dict[name] = content
            tracker.tick()
        tracker.tick_parent()
    return sorted(
        [(info[0], category, info[1]) for category, info in data.items()],
        key=lambda a: (a[-1], a[-2])
    )


def get_text(path: str) -> str:
    text = "".join(
        line.split("|", 1)[-1].strip() for line in
        extract_content(path).split("\n") if not line.startswith("#")
    )
    result = findall("(.*?[.。])", text)
    return "\n".join(result)


if __name__ == '__main__':
    r = prepare_data(join("./data", DATA_PATH))
    print(r)
