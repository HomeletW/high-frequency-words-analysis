import os.path
import sys

import ez_setup

ez_setup.use_setuptools()

from setuptools import setup, find_packages

mainscript = os.path.join(".", "hf_analysis", 'launcher.py')

OPTIONS = {
    "iconfile": "resource/icon.icns",
    "resouce": "",
    "argv_emulation": True,
}

if sys.platform == 'darwin':
    OPTIONS.update(dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options=dict(py2app=dict(argv_emulation=True)),
    ))
elif sys.platform == 'win32':
    OPTIONS.update(dict(
        setup_requires=['py2exe'],
        app=[mainscript],
    ))
else:
    OPTIONS.update(dict(
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
        scripts=[mainscript],
    ))


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="hf_word_analysis",
    version="0.1",
    packages=find_packages(),
    # install_require
    install_requires=[
        "Pillow>=7.1.2",
        "pdf2image>=1.13.1",
        "docx2txt>=0.8",
        "tesserocr>=2.5.1",
        "xlrd>=1.2.0",
        "numpy>=1.18.4",
        "pandas>=1.0.3",
        "sklearn",
        "jieba>=0.42.1",
        "textwrap3=0.9.2",
        "pinyin=0.4.0",
    ],
    # metainfo
    author="HomeletW",
    author_email="homeletwei@gmail.com",
    description="高频词汇分析",
    long_description=readme(),
    url="https://github.com/HomeletW/high-frequency-words-analysis"
)
