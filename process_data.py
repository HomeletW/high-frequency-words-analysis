from typing import List, Optional, Tuple
from os.path import exists, join, abspath
from os import makedirs
import ntpath

from PIL import Image
from tesserocr import PyTessBaseAPI, RIL, iterate_level
from pdf2image import convert_from_path

from prepare_data import extract_content, DATA_PREFIX

# tesseract arguments
TESSDATA_PATH = "./tessdata_best"
TESSERACT_LANG = "chi_sim"
IMAGE_CROP_PARM = (210, 280, 2300, 3050)  # LEFT, TOP, RIGHT, BOTTOM
FORMAT_LENGTH = 50


def process_pdf(output_folder: str,
                path_to_pdf: str,
                path_to_divisor: str,
                tressdata_path: str,
                tesseract_lang: str,
                image_crop_pram: Tuple[int, int, int, int]) -> None:
    # get divisor map
    divisor_map = get_divisor_map(path_to_divisor)
    # get the page range that we need to process
    first_page = min(r[1] for r in divisor_map)
    last_page = max(r[2] for r in divisor_map)
    # temp folder
    temp_folder = join(output_folder, "temp")
    outp_folder = join(output_folder, "output")
    # make sure the temp and output folder exist
    if not exists(temp_folder):
        makedirs(temp_folder)
    if not exists(outp_folder):
        makedirs(outp_folder)
    # first convert all pages of pdf to jpeg
    name_generator = ("Page" for _ in range(1))
    print("处理 PDF 文件中...")
    # divide up the pdf and store them as jpeg
    temp_images_path = convert_from_path(
        path_to_pdf,
        dpi=300, output_folder=temp_folder,
        first_page=first_page, last_page=last_page,
        fmt="jpeg", paths_only=True, output_file=name_generator
    )
    # according to the divisor map, divide the pages to corresponding paragraph
    page_num_map = {extract_page_number(p): p for p in temp_images_path}
    # Use OCR on the images
    with PyTessBaseAPI(path=tressdata_path, lang=tesseract_lang) as api:
        for title, beg, end, sort in divisor_map:
            print(f"正在识别 {title} : ", end="")
            # create a txt file that include all data in this page
            name = "{}_{}_{}.txt".format(DATA_PREFIX, title, sort)
            content_path = join(outp_folder, name)
            with open(content_path, "w+") as f:
                # write header
                f.write("# 可信度 | 行内容 （请校对识别内容，特别注意带有 ？ 的行）\n")
                print(f"{end - beg + 1}/", end="")
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
                    print(".", end="")
                print()


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


def get_divisor_map(path_to_divisor: str) -> List[Tuple[str, int, int, int]]:
    """读取divisor"""
    rules = extract_content(path_to_divisor).split("\n")
    return sorted([process_divisor_rule(rule) for rule in rules if
                   rule and not rule.startswith("#")], key=lambda a: a[1])


def process_divisor_rule(rule: str) -> Optional[Tuple[str, int, int, int]]:
    r = rule.split()
    if len(r) < 4:
        raise Exception("分割格式错误！需要至少4个参数")
    key, beg, end, sort = r[0], int(r[1]), int(r[2]), int(r[3])
    # make sure the rule is correct
    # ie. beg is smaller than end
    assert beg <= end, "分割格式错误！开始页码大于结束页码"
    return key, beg, end, sort


def extract_page_number(path: str) -> int:
    name = ntpath.basename(path).rsplit(".", maxsplit=1)[0]
    return int(name.split("-")[1])


if __name__ == "__main__":
    process_pdf(
        "./data", "./data/data.pdf", "./data/divisor.txt", TESSDATA_PATH,
        TESSERACT_LANG, IMAGE_CROP_PARM
    )
