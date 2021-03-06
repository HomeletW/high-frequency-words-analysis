# -*- coding: utf-8 -*-

from typing import Any, Dict

import xlsxwriter
from pinyin import pinyin

from hf_analysis.parameter import *


def write_excel(path,
                total_summary: Dict[str, Dict[str, Any]],
                detail_summary: Dict[str, Dict[str, Dict[str, int]]],
                sorting,
                tracker,
                show_detail):
    """
    Total summary:
        { tag: { detail } }
    Detail summary:
        { category: { article: { tag: int } }
    """
    tracker.log("正在创建 Excel 文件", prt=True)
    # first write the summary page
    workbook = xlsxwriter.Workbook(path)
    # some format
    title_format = workbook.add_format({"bold": True})
    # create the summary worksheet
    summary = workbook.add_worksheet(name="总结")
    # init accum
    tracker.init_ticker("   进程", "正在输出", 0, len(total_summary) + sum(
        len(tag_details) for tag_details in detail_summary.values()))
    row, col = 0, 0
    max_width = []
    summary.write_string(row, col, "词汇", cell_format=title_format)
    max_width.append(2 * WIDTH_RATIO)
    col += 1
    summary.write_string(row, col, "趋势标签", cell_format=title_format)
    max_width.append(4 * WIDTH_RATIO)
    col += 1
    if show_detail:
        summary.write_string(row, col, "拟合系数", cell_format=title_format)
        max_width.append(4 * WIDTH_RATIO)
        col += 1
        summary.write_string(row, col, "RMSE", cell_format=title_format)
        max_width.append(4 * WIDTH_RATIO)
        col += 1
    # write header
    cat_header = sorted(sorting.items(), key=lambda i: i[1])
    for category, _ in cat_header:
        summary.write_string(row, col, category, cell_format=title_format)
        max_width.append(len(category) * WIDTH_RATIO)
        col += 1
    row += 1
    col = 0
    # write values
    for tag, detail in total_summary.items():
        tracker.update_disc_fill("写入总结 {}".format(tag))
        tracker.tick()
        # write tag
        summary.write_string(row, col, tag)
        max_width[col] = max(len(tag) * WIDTH_RATIO, max_width[col])
        col += 1
        # write label
        label = detail["label"]
        if label is not None:
            label_name = TREND_NAME[label]
            summary.write_string(row, col, label_name)
            max_width[col] = max(len(label_name) * WIDTH_RATIO, max_width[col])
        else:
            summary.write_string(row, col, "-")
            max_width[col] = max(1, max_width[col])
        col += 1
        # write detail
        if show_detail:
            lr = detail["regression"]
            if lr is not None:
                coefficient, _, RMSE = lr
                summary.write_number(row, col, coefficient)
                max_width[col] = max(len(str(coefficient)), max_width[col])
                col += 1
                summary.write_number(row, col, RMSE)
                max_width[col] = max(len(str(RMSE)), max_width[col])
                col += 1
            else:
                summary.write_string(row, col, "-")
                max_width[col] = max(1, max_width[col])
                col += 1
                summary.write_string(row, col, "-")
                max_width[col] = max(1, max_width[col])
                col += 1
        # write
        occurrence = detail["occurrence"]
        for occ in occurrence:
            summary.write_number(row, col, occ)
            max_width[col] = max(len(str(occ)), max_width[col])
            col += 1
        row += 1
        col = 0
    for index, width in enumerate(max_width):
        summary.set_column(index, index, width=width)
    # write detail
    # { category: { tag: { article: int } }
    for category, _ in cat_header:
        tag_details = detail_summary[category]
        work_sheet = workbook.add_worksheet(category)
        row, col = 0, 0
        max_width = []
        work_sheet.write_string(row, col, "词汇", cell_format=title_format)
        max_width.append(2 * WIDTH_RATIO)
        col += 1
        # write header
        header = sorted(
            next(iter(tag_details.values())).keys(),
            key=lambda n: pinyin.get(n, format="strip", delimiter=" ")
        )
        # write header
        for name in header:
            work_sheet.write_string(row, col, name, cell_format=title_format)
            max_width.append(len(name) * WIDTH_RATIO)
            col += 1
        row += 1
        col = 0
        # write values
        for tag, art_detail in tag_details.items():
            tracker.update_disc_fill("写入细节 {}".format(tag))
            tracker.tick()
            work_sheet.write_string(row, col, tag)
            max_width[col] = max(len(tag) * WIDTH_RATIO, max_width[col])
            col += 1
            for name in header:
                val = art_detail[name]
                work_sheet.write_number(row, col, val)
                max_width[col] = max(len(str(val)), max_width[col])
                col += 1
            row += 1
            col = 0
        for index, width in enumerate(max_width):
            work_sheet.set_column(index, index, width=width)
    tracker.log("正在关闭 Excel 文件", prt=True)
    workbook.close()
