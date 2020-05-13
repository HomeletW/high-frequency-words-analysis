from os import listdir
from os.path import isfile, join, splitext
from typing import List, Tuple

DATA_PREFIX = "data"


def extract_content(path: str) -> str:
    """读取一个文件的全部信息"""
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
                    get_text(abs_path),  # the content
                    file_args[1],  # the display name
                    order_index,  # the order index
                )
            )
    data.sort(key=lambda a: (a[2], a[1]))
    return [(content, name) for content, name, _ in data]


def get_text(path: str) -> str:
    return "\n".join(line.split("|", 1)[-1].strip() for line in
                     extract_content(path).split("\n") if
                     not line.startswith("#"))


if __name__ == '__main__':
    data = prepare_data("./data/output")
    print(data)
