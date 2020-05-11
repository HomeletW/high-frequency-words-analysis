import sys
from os import listdir
from os.path import isfile, join, splitext
from typing import List, Tuple

from PIL import Image
from tesserocr import PyTessBaseAPI
from pdf2image import convert_from_path

# import docx

sys.path.append("./")

OUTPUT_FOLDER = "./data/temp/"
DATA_PREFIX = "data"
# tesseract arguments
TESSDATA_PATH = "./tessdata_best"
IMAGE_CROP_PARM = (210, 280, 2300, 3050)  # LEFT, TOP, RIGHT, BOTTOM


def process_pdf(path_to_pdf: str, start_from: int, end_with: int):
    # first convert all pages of pdf to jpeg
    name_generator = ("Page" for _ in range(1))
    temp_images_path = convert_from_path(
        path_to_pdf,
        dpi=300,
        output_folder=OUTPUT_FOLDER,
        first_page=start_from,
        last_page=end_with,
        fmt="tiff",
        paths_only=True,
        output_file=name_generator
    )
    conf_sum = 0
    # Use OCR on the images
    with PyTessBaseAPI(path=TESSDATA_PATH, lang="chi_sim") as api:
        for img_path in temp_images_path:
            print("====================")
            # first we do some pre-processing on the image
            img = Image.open(img_path)
            # convert to gray scale and apply binarization
            img = img.convert("L").point(lambda x: 0 if x < 180 else 255, "1")
            img = img.crop(IMAGE_CROP_PARM)
            # use Tesseract
            api.SetImage(img)
            api.Recognize()
            # get the recognized text and the mean confidence value
            text = api.GetUTF8Text()
            conf = api.MeanTextConf()
            # process the text
            # remove the spaces but not newline
            text = text.replace(" ", "")
            print(text)
            print(conf)
            conf_sum += conf
    print(conf_sum / len(temp_images_path))


def extract_content(path: str) -> str:
    """读取一个文件的全部信息"""
    if path.endswith(".doc") or path.endswith(".docx"):
        # doc = docx.Document(path)
        # content = "".join(par.text for par in doc.paragraphs)
        return ""
    else:
        with open(path, encoding="utf8") as f:
            return f.read()


def load_suggestion_word(path: str) -> List[str]:
    """装载用户自定建议词典"""
    ls = extract_content(path).split("\n")
    ls.remove("")
    return ls


def prepare_data(root_path: str) -> List[Tuple[str, str]]:
    data = []
    for file_name in listdir(root_path):
        # get the abs path
        abs_path = join(root_path, file_name)
        # get the args
        file_args = splitext(file_name)[0].split("_")
        # the first args must be DATA_PREFIX and must have two arg
        if len(file_args) < 2 or file_args[0] != DATA_PREFIX:
            continue
        elif not isfile(abs_path):
            continue
        else:
            order_index = int(file_args[2]) if len(file_args) >= 3 else 0
            data.append(
                (
                    extract_content(abs_path),  # the content
                    file_args[1],  # the display name
                    order_index,  # the order index
                )
            )
    data.sort(key=lambda a: (a[2], a[1]))
    return [(content, name) for content, name, _ in data]


if __name__ == "__main__":
    process_pdf(
        "./data/data.pdf", start_from=24, end_with=30
    )
