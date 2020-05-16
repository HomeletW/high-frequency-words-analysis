import ntpath
from os import listdir, makedirs
from os.path import abspath, exists, isfile, join
from textwrap import wrap
from typing import List, Tuple

import pandas as pd
import tesserocr
from PIL import Image
from pdf2image import convert_from_path
from tesserocr import PyTessBaseAPI, RIL, iterate_level

from hf_analysis.parameter import *
from hf_analysis.processing.prepare_data import extract_content, \
    get_name_extension

AVAILABLE_LANG = list(filter(lambda a: "/" not in a,
                             tesserocr.get_languages(TESSDATA_PATH)[1]))


def process(path_to_index: str,
            path_to_additional_parm: str,
            output_folder: str,
            dpi: int,
            cov_format: str,
            default_lang: str,
            tracker):
    """format 为 [(title, file_path, cat, sort, beg, end), ...]"""
    # make sure the data folder exist
    data_folder = join(output_folder, DATA_PATH)
    temp_folder = join(output_folder, TEMP_PATH)
    reso_folder = join(output_folder, RESOURCE_PATH)
    if not exists(data_folder):
        makedirs(data_folder)
    # get the additional pram
    if path_to_additional_parm is None or path_to_additional_parm == "":
        parm_map = {}
    else:
        parm_map = get_additional_pram(path_to_additional_parm)
    # get the index map
    index_map = get_index_map(path_to_index)
    # init parent progress of tracker
    tracker.init_parent_progress(
        "预处理父程序", 0,
        sum(end - beg + 1 if beg is not None and end is not None else 1
            for _, _, _, _, beg, end, _ in index_map)
    )
    # we process file by file
    file_map = {}
    for title, file_path, cat, sort, beg, end, parm in index_map:
        # if the parm is empty, we replace it with the default value
        if len(parm) == 0 and file_path in parm_map:
            parm = parm_map[file_path]
        file_path = join(reso_folder, file_path)
        if file_path not in file_map:
            file_map[file_path] = []
        file_map[file_path].append((title, cat, sort, beg, end, parm))

    for path, setup in file_map.items():
        name, extension = get_name_extension(path)
        if extension in [".pdf"]:
            tracker.log("正在处理 PDF 文件 : {} ...".format(path), prt=True)
            if not exists(temp_folder):
                makedirs(temp_folder)
            process_pdf(path, temp_folder, data_folder, dpi, cov_format,
                        default_lang, setup, tracker)
        else:
            tracker.log("正在处理 文本 文件 : {} ...".format(path), prt=True)
            process_text(path, data_folder, setup, tracker)
    total_time = tracker.time_elapsed(use_time_accum=True)
    tracker.clear_time_accum()
    tracker.reset_ticker()
    tracker.reset_parent()
    tracker.log("处理完成！ 用时 : {} 秒".format(total_time), prt=True)


def process_text(path_to_text: str,
                 data_folder: str,
                 setup: List[Tuple[str, str, int, int, int, dict]],
                 tracker) -> None:
    content = extract_content(path_to_text)
    # create a file that include all data in this page
    for title, cat, sort, beg, end, parm in setup:
        if beg is not None or end is not None:
            from hf_analysis.ui.tk_object import TRACKER_LOG_ERROR
            tracker.log("   目前文本文档不支持分页！", tp=TRACKER_LOG_ERROR, prt=True)
        name = "{}_{}_{}_{}.txt".format(DATA_PREFIX, sort, cat, title)
        content_path = join(data_folder, name)
        tracker.log("   正在写入 {} -> {} ...".format(title, name), prt=True)
        with open(content_path, "w+") as f:
            # write a div for easy identify
            f.write("#" + "=" * FORMAT_LENGTH + "\n")
            # write the path of this page
            f.write("#文件地址: {}\n".format(abspath(path_to_text)))
            # write the content
            content_list = wrap(content, width=FORMAT_LENGTH)
            for line in content_list:
                f.write("  ---.-- | {0:}\n".format(line))
            amount = end - beg + 1 if beg is not None and end is not None else 1
            tracker.tick_parent(amount=amount)


def pdf_to_jpeg(path_to_pdf: str, temp_folder: str, dpi: int, cov_format: str,
                setup) -> \
        List[str]:
    # get the page range that we need to process
    first_page = min(r[3] for r in setup)
    last_page = max(r[4] for r in setup)
    # find in the temp folder that is the pdf processed already
    name, _ = get_name_extension(ntpath.basename(path_to_pdf))
    # find the existing file
    files = [f for f in listdir(temp_folder) if isfile(join(temp_folder, f))]
    processed = {extract_page_number(f): join(temp_folder, f) for f in files if
                 f.startswith(name)}
    subsets, relev = get_relevant_subset(processed, first_page, last_page)
    name_generator = ("{}".format(name) for _ in range(1))
    # iterate through the subset
    paths = [processed[index] for index in relev]
    for start, end in subsets:
        temp_images_path = convert_from_path(
            pdf_path=path_to_pdf,
            dpi=dpi, output_folder=temp_folder,
            first_page=start, last_page=end,
            fmt=cov_format, paths_only=True, output_file=name_generator
        )
        paths.extend(temp_images_path)
    return paths


def get_relevant_subset(processed: dict, first_page: int, last_page: int) -> \
        Tuple[List[Tuple[int, int]], List[int]]:
    relev = [i for i in processed if first_page <= i <= last_page]
    if len(relev) == 0:
        # we need to fetch all
        return [(first_page, last_page)], relev
    relev.sort()
    middle = [(relev[i] + 1, relev[i + 1] - 1) for i in range(len(relev) - 1) if
              (relev[i + 1] - 1) - (relev[i] + 1) >= 0]
    # add first and last group
    if first_page < relev[0]:
        if (relev[0] - 1) - first_page >= 0:
            middle = [(first_page, relev[0] - 1)] + middle
    if relev[-1] < last_page:
        if last_page - (relev[-1] + 1) >= 0:
            middle = middle + [(relev[-1] + 1, last_page)]
    return middle, relev


def process_pdf(path_to_pdf: str,
                temp_folder: str,
                data_folder: str,
                dpi: int,
                cov_format: str,
                default_lang: str,
                setup: List[Tuple[str, str, int, int, int, dict]],
                tracker) -> None:
    tracker.log("   转换 PDF -> {} ...".format(cov_format), prt=True)
    tracker.init_ticker("   进程", "正在扫描 PDF", 0, 1)
    # first convert all pages of pdf to jpeg
    temp_img_path = pdf_to_jpeg(path_to_pdf, temp_folder, dpi, cov_format,
                                setup)
    tracker.tick(amount=1)
    # according to the divisor map, divide the pages to corresponding paragraph
    page_num_map = {extract_page_number(p): p for p in temp_img_path}
    # Use OCR on the images
    with PyTessBaseAPI(path=TESSDATA_PATH, lang=default_lang) as api:
        for title, cat, sort, beg, end, parm in setup:
            if "LANG" in parm:
                api.InitFull(path=TESSDATA_PATH, lang=parm["LANG"])
            image_crop_pram = parm.get("CROP", None)
            # create a txt file that include all data in this page
            name = "{}_{}_{}_{}.txt".format(DATA_PREFIX, sort, cat, title)
            content_path = join(data_folder, name)
            tracker.log("   正在识别 [lang={}] {} -> {} ...".format(
                api.GetInitLanguagesAsString(), title, name), prt=True)
            with open(content_path, "w+") as f:
                # write header
                f.write("# 可信度 | 行内容 （请校对识别内容，特别注意带有 ？ 的行）\n")
                tracker.init_ticker("   进程", "正在识别: {}".format(title), 0,
                                    end - beg + 1)
                for i in range(beg, end + 1):
                    page_path = page_num_map[i]
                    content = get_content(api, page_path, image_crop_pram)
                    avg_conf = sum(conf for _, conf in content) / len(content)
                    # write a div for easy identify
                    f.write(
                        "#" + " 页码: {0:}, 平均可信度: {1:3.2f} ".format(
                            i, avg_conf).center(FORMAT_LENGTH, "=") + "\n"
                    )
                    # write the path of this page
                    f.write("#文件地址: {}\n".format(abspath(page_path)))
                    for text, conf in content:
                        indi = "?" if conf < avg_conf else " "
                        f.write(
                            "{0:s} {1:3.2f} | {2:}\n".format(indi, conf, text)
                        )
                    tracker.tick()
                    tracker.tick_parent()


def get_content(api, img_path: str,
                image_crop_pram: Tuple[int, int, int, int]) -> \
        List[Tuple[str, float]]:
    # first we do some pre-processing on the image
    img = Image.open(img_path)
    # convert to gray scale and apply binarization
    img = img.convert("L").point(lambda x: 0 if x < 180 else 255, "1")
    if image_crop_pram is not None:
        img = img.crop(image_crop_pram)
    # use Tesseract to recognize the texts
    api.SetImage(img)
    api.Recognize()
    # build the data
    page_text = []
    ri = api.GetIterator()
    level = RIL.TEXTLINE
    for r in iterate_level(ri, level):
        line = r.GetUTF8Text(level)
        conf = r.Confidence(level)
        # process the text, remove the space, and newline
        line = line.replace(" ", "").replace("\n", "")
        page_text.append((line, conf))
    return page_text


def get_additional_pram(path_to_additional_pram: str) -> dict:
    df = pd.read_excel(path_to_additional_pram)
    return {str(r[0]): process_pram(r[1:]) for _, r in df.iterrows()}


def get_index_map(path_to_index: str) -> \
        List[Tuple[str, str, str, int, int, int, dict]]:
    """
    读取divisor
    返回 format 为
    [(title, file_path, category, sort_index, start_index, end_index), ...]
    """
    df = pd.read_excel(path_to_index)
    index = [process_index_rule(r) for _, r in df.iterrows()]
    return sorted(index, key=lambda a: (a[3]))


def process_index_rule(r) -> Tuple[str, str, str, int, int, int, dict]:
    """
    format 为
    [(title, file_path, cat, sort, beg, end, pram), ...]
    #  str     str      str   int  int  int  dict
    """
    if len(r) < 6:
        raise Exception("分割格式错误！需要至少6个参数")
    title, file_path, cat, sort, beg, end = r[:6]
    pram = process_pram(r[6:])
    sort = int(sort)
    if pd.isna(beg) or pd.isna(end):
        beg, end = None, None
    else:
        beg, end = int(beg), int(end)
        assert beg <= end, "分割格式错误！开始页码大于结束页码"
    return title, file_path, cat, sort, beg, end, pram


def process_pram(s: list) -> dict:
    pram = {}
    for cell in s:
        if pd.isna(cell):
            continue
        for par in str(cell).split("|"):
            key, value = par.split("=", 1)
            value = value.replace("“", "\"").replace("”", "\"")
            pram[key.upper()] = eval(value)
    return pram


def extract_page_number(path: str) -> int:
    name = ntpath.basename(path).rsplit(".", maxsplit=1)[0]
    return int(name.split("-")[1])


if __name__ == "__main__":
    from hf_analysis.ui.tk_object import ProgressTracker

    t = ProgressTracker(True, None)
    process("./data/debug_index.xlsx",
            "./data/additioanl_pram.xlsx",
            "./data",
            300,
            "chi_sim",
            t)
