from typing import List, Optional, Tuple
from os.path import exists
from os import makedirs

from PIL import Image
from tesserocr import PyTessBaseAPI, RIL, iterate_level
from pdf2image import convert_from_path

from prepare_data import extract_content

# tesseract arguments
TESSDATA_PATH = "./tessdata_best"
TESSERACT_LANG = "chi_sim"
IMAGE_CROP_PARM = (210, 280, 2300, 3050)  # LEFT, TOP, RIGHT, BOTTOM


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
    # make sure the output folder exist
    if not exists(output_folder):
        makedirs(output_folder)
    # first convert all pages of pdf to jpeg
    name_generator = ("Page" for _ in range(1))
    temp_images_path = convert_from_path(
        path_to_pdf,
        dpi=300,
        output_folder=output_folder,
        first_page=first_page,
        last_page=last_page,
        fmt="jpeg",
        paths_only=True,
        output_file=name_generator
    )
    conf_sum = 0
    # Use OCR on the images
    with PyTessBaseAPI(path=tressdata_path, lang=tesseract_lang) as api:
        for img_path in temp_images_path:
            print("=========")
            # first we do some pre-processing on the image
            img = Image.open(img_path)
            # convert to gray scale and apply binarization
            img = img.convert("L").point(lambda x: 0 if x < 180 else 255, "1")
            if image_crop_pram is not None:
                img = img.crop(image_crop_pram)
            # use Tesseract
            api.SetImage(img)
            api.Recognize()

            ri = api.GetIterator()
            level = RIL.TEXTLINE
            for r in iterate_level(ri, level):
                line = r.GetUTF8Text(level)
                conf = r.Confidence(level)
                # process the text, remove the space, not newline
                line = line.replace(" ", "")
                print(line)
                print(conf)
    print(conf_sum / len(temp_images_path))


def get_divisor_map(path_to_divisor: str) -> List[Tuple[str, int, int, int]]:
    """读取divisor"""
    rules = extract_content(path_to_divisor).split("\n")
    return sorted([process_divisor_rule(rule) for rule in rules if
                   rule and not rule.startswith("#")], key=lambda a: a[1])


def process_divisor_rule(rule: str) -> Optional[Tuple[str, int, int, int]]:
    r = rule.split()
    if len(r) < 4:
        raise Exception("分割格式错误！")
    key, beg, end, sort = r[0], int(r[1]), int(r[2]), int(r[3])
    return key, beg, end, sort


if __name__ == "__main__":
    process_pdf(
        "./data/temp/", "./data/data.pdf", "./data/divisor.txt", TESSDATA_PATH,
        IMAGE_CROP_PARM
    )
