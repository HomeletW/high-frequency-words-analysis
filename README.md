# 高频词汇分析 （hf_word_analysis)

## 项目概述

<img src="resource/project_overview.png" alt="project overview">

### 功能

## 项目依赖

`Pillow` python 图像处理

`pdf2image` pdf >> png, jpeg, tiff, ...

`docx2txt` 读取 word 文件

`XlsxWriter` 读取与编辑 excel 文件

`sklearn` 训练线性回归模型

`tesseract-ocr` 光学识别字符

`tesserocr` python 调用 tesseract-ocr API

`jieba` 中文分词，关键词抽取

## 如何安装

### MacOs

<h4 id="python_install"> python 与 pip 安装 </h4>

请前往 <a href="https://www.python.org/downloads/">python 官方下载网站</a> 
进行下载，点击下载 python 3.8 或以上的版本（注意要 64bit 版）。下载后双击运行文件，一直点击下一步直到安装结束。

<img src="resource/python_install_success.png" alt="python install success">

接下来我们验证 python 与 pip 是否被正确安装。

首先<a href="#h2_open_terminal">打开 终端.app（Terminal.app）</a>，打开聚焦搜索（同时按下 Command + 空格键），输入 Terminal.app

<img src="resource/terminal_open.png" alt="terminal open">

接下来输入 `python3 -V` 和 `pip3 -V`

````
➜  ~ python3 -V
Python 3.8.3
➜  ~ pip3 -V
pip 20.0.2 from ... (python 3.8)
````

如果返回结果类似于 `Python 3.8.3` 和 `pip 20.0.2` 说明您已经成功安装 Python 3.8.3！

<h4 id="homebrew_install"> Homebrew 安装 </h4>

在安装 高频词汇分析 之前我们需要安装几个项目依赖库，我们将使用包管理工具 Homebrew 来协助我们安装。
请首先打开<a href="#h2_open_terminal">终端（Terminal.app）</a>且输入以下命令：

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

如果程序提醒 "Press Enter to continue"，请按下回车键。以下是示例结果：
````
➜  ~ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
==> This script will install:
/usr/local/bin/brew
/usr/local/share/doc/homebrew
/usr/local/share/man/man1/brew.1
/usr/local/share/zsh/site-functions/_brew
/usr/local/etc/bash_completion.d/brew
/usr/local/Homebrew

Press RETURN to continue or any other key to abort  ---> 请按 Enter 键 <---
==> Downloading and installing Homebrew...
...
==> Installation successful!
...
````

<h4 id="poppler_install"> poppler 安装 </h4>

接下来请在<a href="#h2_open_terminal">终端（Terminal.app）</a>对话框输入以下命令来安装 `poppler` 库（提供关于 PDF 处理支持）。

`brew install poppler`

以下是示例结果：

````
➜  ~ brew install poppler 
==> Downloading https://homebrew.bintray.com/bottles/poppler-0.88.0.catalina.bot
...
==> Pouring poppler-0.88.0.catalina.bottle.tar.gz
🍺  /usr/local/Cellar/poppler/0.88.0: 459 files, 24.9MB
````

<h4 id="tesseract_install"> tesseract 安装 </h4>

接下来请在<a href="#h2_open_terminal">终端（Terminal.app）</a>对话框输入以下命令来安装 `tesseract` 库（提供关于光学字符识别（OCR）支持）。

`brew install tesseract`

以下是示例结果：
````
➜  ~ brew install tesseract 
==> Downloading https://homebrew.bintray.com/bottles/tesseract-4.1.1.catalina.bo
...
==> Pouring tesseract-4.1.1.catalina.bottle.tar.gz
==> Caveats
This formula contains only the "eng", "osd", and "snum" language data files.
If you need any other supported languages, run `brew install tesseract-lang`.
==> Summary
🍺  /usr/local/Cellar/tesseract/4.1.1: 65 files, 29.6MB
````

<h4 id="poppler_install"> 主体程序安装 </h4>

接下来我们将安装主体程序，前往<a href="https://github.com/HomeletW/high-frequency-words-analysis">
高频词汇分析 github 主页</a>（或者您已经在这个页面，请翻到页面顶端），
点击绿色按钮 `Clone or download` 然后选择 `Download ZIP`，然后请稍后zip文件包的下载（大约 100 MB）。

<img src="resource/download_zip.png" alt="zip download">

接下来将下载好的 zip 文件移动到您喜欢的位置（例如，桌面）然后双击解压，并且将解压好的文件夹改成喜欢的名字。

！！注意：一旦程序设定完成，将不能改变该文件夹地址以及名字，所以要现在设置完成 ！！

双击打开该文件夹，找到 `install_script.sh` 文件。

现在请在<a href="#h2_open_terminal">终端（Terminal.app）</a>对话框输入 `sh` 并且把 `install_script.sh` 拖入对话框中，然后按下回车键。

<img src="resource/drag_install_script.gif" alt="drag install script">

以下是示例结果：
````
➜  ~ sh /Users/homelet/Desktop/high-frequency-words-analysis-master/install_script.sh
Working in /Users/homelet/Desktop/high-frequency-words-analysis-master
Installing Virtuelenv...
...
Creating Virtuelenv enviroment...
...
Installing Dependencies...
...
Installing collected packages: ...
Successfully installed ...
Prepare to build App...
...
*** creating application bundle: 高频词汇分析 ***
...
Done!
Finnished!
安装结束！已在 dist 文件夹里创造 高频词汇分析.app
````

恭喜您，您已经成功安装了高频词汇分析！

在结束安装之后，会自动弹出一个含有 <u>高频词汇分析.app</u> 的窗口，双击 <u>高频词汇分析.app</u> 来测试程序运行，
如果运行成功，程序主页面将会展示。

如果没有发现<u>高频词汇分析.app</u>，可能有以下几个原因:
1. 窗口失败弹出，请检查在目录下的 dist 文件夹，
2. 如果在 dist 文件夹还未发现<u>高频词汇分析.app</u>，说明安装失败，请联系开发者来获取更多信息，或者重新尝试上一步。


运行成功之后可以把 <u>高频词汇分析.app</u> 文件拖入 程序（Application）文件夹，来快速访问。

## 常见问题

<h3 id="h2_open_terminal">1. 如何打开 终端.app（Terminal.app)</h3>

<h5>方法1：</h5>
打开聚焦搜索（同时按下 Command + 空格键），输入 终端.app（Terminal.app），按下回车即可打开。

<img src="resource/terminal_open.png" alt="terminal open">

<h5>方法2：</h5>
Application 文件夹并搜索 终端.app（Terminal.app），双击即可打开。

<h3 id="h2_solve_poppler">2. Unable to get Page Count, is poppler installed?</h3>

首先<a href="#h2_open_terminal">打开终端（Terminal.app）</a> 输入以下指令：

`brew unlink poppler && brew link poppler`




