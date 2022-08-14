# -*- coding: utf-8 -*-
import pathlib
from os import makedirs
from os.path import abspath, basename
from textwrap import wrap
from typing import Optional

from PIL import Image
from pdf2image import convert_from_path
from tesserocr import PyTessBaseAPI, RIL, iterate_level

from hf_analysis.processing.load_data import *


def process(path_to_index: str,
            path_to_additional_parm: str,
            output_folder: str,
            dpi: int,
            cov_format: str,
            engine: bool,
            default_lang: str,
            tessdata_path: str,
            tracker):
    """format 为 [(title, file_path, cat, sort, beg, end), ...]"""
    # make sure the data folder exist
    data_folder = join(output_folder, DATA_PATH)
    temp_folder = join(output_folder, TEMP_PATH)
    reso_folder = join(output_folder, RESOURCE_PATH)
    if not exists(reso_folder):
        raise ValueError("根目录没有 resource 文件夹！")
    if not exists(data_folder):
        makedirs(data_folder)
    # get the additional pram
    if path_to_additional_parm is None or path_to_additional_parm == "":
        parm_map = {}
    else:
        parm_map = get_additional_pram(path_to_additional_parm, tracker)
    # get the index map
    index_map = get_index_map(path_to_index, tracker)
    tracker.log("正在分配任务", prt=True)
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
    # init the ticker
    tracker.init_ticker(
        "   进程", "正在进行预处理", 0,
        sum(end - beg + 1 if beg is not None and end is not None else 1
            for _, _, _, _, beg, end, _ in index_map)
    )
    for path, setup in file_map.items():
        name, extension = splitext(path)
        if extension in [".pdf"]:
            tracker.log("正在处理 PDF 文件 : {}".format(path), prt=True)
            if not exists(temp_folder):
                makedirs(temp_folder)
            process_pdf(path, temp_folder, data_folder, dpi, cov_format, engine,
                        default_lang, tessdata_path, setup, tracker)
        else:
            tracker.log("正在处理 文本 文件 : {}".format(path), prt=True)
            process_text(path, data_folder, setup, tracker)


def process_text(path_to_text: str,
                 data_folder: str,
                 setup: List[Tuple[str, str, int, int, int, dict]],
                 tracker) -> None:
    content = extract_content(path_to_text)
    # create a file that include all data in this page
    for title, cat, sort, beg, end, parm in setup:
        tracker.update_disc_fill("写入 {} <{}>".format(title, cat))
        if beg is not None or end is not None:
            tracker.log("   目前文本文档不支持分页！", tp=TRACKER_LOG_WARNING, prt=True)
        name = "{}_{}_{}_{}.txt".format(DATA_PREFIX, sort, cat, title)
        content_path = join(data_folder, name)
        tracker.log("   正在处理 {}".format(title), prt=True)
        with open(content_path, "w+", encoding="utf8") as f:
            # write a div for easy identify
            f.write("#" + "=" * FORMAT_LENGTH + "\n")
            # write the path of this page
            f.write("#文件地址: {}\n".format(abspath(path_to_text)))
            # write the content
            content_list = wrap(content, width=FORMAT_LENGTH)
            for line in content_list:
                f.write("  ---.-- | {0:}\n".format(line))
        tracker.tick()


def scan_pdf(path_to_pdf: str,
             temp_folder: str,
             dpi: int,
             cov_format: str,
             engine: bool,
             setup, tracker) -> Dict[int, str]:
    tracker.log(
        "   转换 pdf -> {} [utilizing_thread={}]".format(
            cov_format, USABLE_THREAD),
        prt=True)
    # get the page range that we need to process
    first_page = min(r[3] for r in setup)
    last_page = max(r[4] for r in setup)
    # find in the temp folder that is the pdf processed already
    name, _ = splitext(basename(path_to_pdf))
    # find the existing file
    processed = {}
    for f in listdir(temp_folder):
        p = join(temp_folder, f)
        if not isfile(p):
            continue
        info = extract_info(f)
        if info is None:
            continue
        prefix, f_dpi, page_number, format_ = info
        if prefix == name and f_dpi == dpi and format_.endswith(cov_format):
            # we got this file already
            processed[page_number] = str(p)
    subsets, relev = get_relevant_subset(processed, first_page, last_page)
    total_page = sum(e - s + 1 for s, e in subsets)
    name_generator = ("{}-{}".format(name, dpi) for _ in range(total_page))
    tracker.update_disc_fill("扫描 {}".format(basename(path_to_pdf)))
    tracker.set_indeterminate(True)
    # iterate through the subset
    paths = {index: processed[index] for index in relev}
    # import tkinter.messagebox
    # tkinter.messagebox.showinfo("Test {}".format(paths),
    #                             f":???")
    for start, end in subsets:
        # tkinter.messagebox.showinfo("Test {}".format(paths),
        #                             f"start: {start}, end: {end}")
        temp_images_path = convert_from_path(
            pdf_path=path_to_pdf,
            dpi=dpi, output_folder=temp_folder,
            first_page=start, last_page=end,
            fmt=cov_format, paths_only=True, output_file=name_generator,
            use_pdftocairo=engine,
            poppler_path=pathlib.PurePath(POPPLER_PATH),
            thread_count=USABLE_THREAD,
        )
        paths.update({extract_page_number(p): p for p in temp_images_path})
    tracker.set_indeterminate(False)
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
                engine: bool,
                default_lang: str,
                tessdata_path: str,
                setup: List[Tuple[str, str, int, int, int, dict]],
                tracker) -> None:
    # first convert all pages of pdf to jpeg
    page_num_map = scan_pdf(path_to_pdf,
                            temp_folder,
                            dpi,
                            cov_format,
                            engine,
                            setup, tracker)

    # Use OCR on the images
    with PyTessBaseAPI(path=tessdata_path, lang=default_lang) as api:
        total_conf = 0
        for title, cat, sort, beg, end, parm in setup:
            if "LANG" in parm:
                api.InitFull(path=tessdata_path, lang=parm["LANG"])
            image_crop_pram = parm.get("CROP", None)
            # create a txt file that include all data in this page
            name = "{}_{}_{}_{}.txt".format(DATA_PREFIX, sort, cat, title)
            content_path = join(data_folder, name)
            tracker.log("   正在识别 [lang={}] {}".format(
                api.GetInitLanguagesAsString(), title), prt=True)
            with open(content_path, "w+", encoding="utf8") as f:
                # write header
                f.write("# 可信度 | 行内容 （请校对识别内容，特别注意带有 ？ 的行）\n")
                tracker.update_disc_fill("识别 {} <{}>".format(title, cat))
                total_page_conf = 0
                for i in range(beg, end + 1):
                    page_path = page_num_map[i]
                    content = get_content(api, page_path,
                                          image_crop_pram,
                                          tracker)
                    if len(content) != 0:
                        avg_conf = sum(conf for _, conf in content) / len(
                            content)
                    else:
                        avg_conf = 0
                    total_page_conf += avg_conf
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
                total_page = end - beg + 1
                pg_avg_conf = 0 if total_page == 0 else \
                    total_page_conf / total_page
                f.write("#" + "总体平均可信度 : {:3.2f}".format(pg_avg_conf).center(
                    FORMAT_LENGTH, "="))
                total_conf += pg_avg_conf
        total_avg_conf = 0 if len(setup) == 0 else total_conf / len(setup)
        tracker.log("总体平均可信度 : {}".format(total_avg_conf), prt=True)


def get_content(api, img_path: str,
                image_crop_pram: Tuple[int, int, int, int], tracker) -> \
        List[Tuple[str, float]]:
    # first we do some pre-processing on the image
    img = Image.open(img_path)
    # convert to gray scale and apply binarization
    img = img.convert("L").point(lambda x: 0 if x < 180 else 255, "1")
    if image_crop_pram is not None:
        img = img.crop(image_crop_pram)
    # use tesseract to recognize the texts
    api.SetImage(img)
    api.Recognize()
    # build the data
    page_text = []
    ri = api.GetIterator()
    level = RIL.TEXTLINE
    for r in iterate_level(ri, level):
        try:
            line = r.GetUTF8Text(level)
            conf = r.Confidence(level)
            # process the text, remove the space, and newline
            line = line.replace(" ", "").replace("\n", "")
            page_text.append((line, conf))
        except RuntimeError as e:
            tracker.log("No text Returned on this line.", tp=TRACKER_LOG_ERROR,
                        exc_info=e)
    return page_text


def extract_page_number(path: str) -> int:
    name = str(basename(path).rsplit(".", maxsplit=1)[0])
    return int(name.split("-")[2])


def extract_info(path: str) -> Optional[Tuple[str, int, int, str]]:
    name, format_ = splitext(basename(path))
    seg = name.split("-")
    if len(seg) != 3:
        return None
    prefix, dpi, page_number = seg
    return str(prefix), int(dpi), int(page_number), str(format_)
