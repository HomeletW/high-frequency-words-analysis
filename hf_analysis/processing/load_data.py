from os import listdir
from os.path import basename, exists, isfile, join, splitext
from re import findall
from typing import Dict, List, Tuple

import pandas as pd
from docx2txt import process

from hf_analysis.parameter import *


def extract_content(path: str) -> str:
    """读取一个文件的全部信息"""
    _, extension = splitext(path)
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


def prepare_data(root_path: str, index_path: str, tracker) -> \
        Tuple[Dict[str, Dict[str, str]], Dict[str, int]]:
    """
    返回格式为：
        { category_name: ({ article_name: content }, order_index) }
    """
    data_path = join(root_path, DATA_PATH)
    if not exists(data_path):
        raise ValueError("根目录没有 data 文件夹! 请先进行预处理，或选择其他根目录！")
    data = {}
    ordering = {}
    dirs = listdir(data_path)
    index_map = get_index_map(path_to_index=index_path,
                              tracker=tracker)
    index_file_name = [
        "{}_{}_{}_{}".format(DATA_PREFIX, sort_index, category, title) for
        title, _, category, sort_index, _, _ in index_map
    ]
    tracker.init_ticker("   进程", "正在处理", 0, len(dirs))
    for file_name in dirs:
        # get the abs path
        abs_path = join(data_path, file_name)
        # basename
        base_name = basename(file_name)
        # get the args
        file_args = splitext(file_name)[0].split("_")
        # the first args must be DATA_PREFIX and must have two arg
        if len(file_args) < 4 or file_args[0] != DATA_PREFIX:
            tracker.log("跳过 {} 因为文件名不符合规范".format(file_name), prt=True)
            continue
        elif not isfile(abs_path):
            tracker.log("跳过 {} 因为无此文件".format(file_name), prt=True)
            continue
        elif base_name not in index_file_name:
            tracker.log("跳过 {} 因为文件不在 index 里".format(file_name), prt=True)
            continue
        else:
            index_file_name.remove(base_name)
            tracker.update_disc_fill("处理 {}".format(file_name))
            content = get_text(abs_path)
            category = file_args[2]
            name = file_args[3]
            order_index = int(file_args[1])
            tracker.log("处理 {} [category={}, name={}, order_index={}]".format(
                file_name, category, name, order_index), prt=True)
            if category not in data:
                data[category] = {}
                ordering[category] = order_index
            c_dict = data[category]
            o_index = ordering[category]
            if o_index != order_index:
                tracker.log(
                    "读取数据错误！ 相同类别, 不同排序, 自动分类成 {} : "
                    "[file={}, index={}, expected_index={}]".format(
                        o_index, abs_path, order_index, o_index
                    ),
                    tp=TRACKER_LOG_WARNING, prt=True)
            c_dict[name] = content
            tracker.tick()
    return data, ordering


def get_text(path: str) -> str:
    text = "".join(
        line.split("|", 1)[-1].strip() for line in
        extract_content(path).split("\n") if not line.startswith("#")
    )
    result = findall("(.*?[.。])", text)
    return "\n".join(result)


def get_additional_pram(path_to_additional_pram: str, tracker) -> dict:
    df = pd.read_excel(path_to_additional_pram)
    return {str(r[0]): process_pram(r[1:], tracker) for _, r in df.iterrows()}


def get_index_map(path_to_index: str, tracker) -> \
        List[Tuple[str, str, str, int, int, int, dict]]:
    """
    读取divisor
    返回 format 为
    [(title, file_path, category, sort_index, start_index, end_index), ...]
    """
    df = pd.read_excel(path_to_index)
    index = [process_index_rule(r, tracker) for _, r in df.iterrows()]
    return sorted(index, key=lambda a: (a[3]))


def process_index_rule(r, tracker) -> Tuple[str, str, str, int, int, int, dict]:
    """
    format 为
    [(title, file_path, cat, sort, beg, end, pram), ...]
    #  str     str      str   int  int  int  dict
    """
    if len(r) < 6:
        raise Exception("分割格式错误！需要至少6个参数")
    title, file_path, cat, sort, beg, end = r[:6]
    pram = process_pram(r[6:], tracker)
    sort = int(sort)
    if pd.isna(beg) or pd.isna(end):
        beg, end = None, None
    else:
        beg, end = int(beg), int(end)
        assert beg <= end, "分割格式错误！开始页码大于结束页码"
    return title, file_path, cat, sort, beg, end, pram


def process_pram(s: list, tracker) -> dict:
    pram = {}
    for cell in s:
        if pd.isna(cell):
            continue
        for par in str(cell).split("|"):
            key, value = par.split("=", 1)
            key = key.strip().upper()
            value = process_pram_value(key, value.strip(), tracker)
            if value is not None:
                pram[key.upper()] = value
    return pram


def process_pram_value(key, value, tracker):
    if key in [ADDI_PARM_CROP]:
        v = value.split("/")
        if len(v) < 4:
            tracker.log(
                "额外参数值加载错误，长度应至少为 4 [key='{}', value='{}']".format(key, value),
                tp=TRACKER_LOG_WARNING, prt=True)
            return None
        return int(v[0]), int(v[1]), int(v[2]), int(v[3])
    elif key in [ADDI_PARM_LANG]:
        return str(value)
    else:
        return None
