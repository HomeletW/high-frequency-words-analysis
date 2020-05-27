# 高频词汇分析 （hf_word_analysis)

- <a href="#项目概述">项目概述</a>
- <a href="#界面介绍">界面与功能介绍</a>
    - <a href="#参数面板及可配置参数">参数面板及可配置参数</a>
    - <a href="#进程面板">进程面板</a>
    - <a href="#控制面板">控制面板</a>
    - <a href="#状态面板">状态面板</a>
- <a href="#分析流程介绍">分析流程介绍</a>
    - <a href="#创建根目录">创建根目录</a>
    - <a href="#准备数据">准备数据</a>
    - <a href="#创建索引">创建索引</a>
        - <a href="#索引文件格式">索引文件格式</a>
        - <a href="#附加参数格式">附加参数格式</a>
    - <a href="#预处理">预处理</a>
    - <a href="#校对预处理">校对预处理</a>
    - <a href="#装载数据">装载数据</a>
    - <a href="#抽取词汇">抽取词汇</a>
    - <a href="#初步检查词汇">初步检查词汇</a>
    - <a href="#统计分析">统计分析</a>
    - <a href="#输出">输出</a>
- <a href="#如何安装">如何安装</a>
    - <a href="#MacOs">MacOs</a>
        - <a href="#python 与 pip 安装">python 与 pip 安装</a>
        - <a href="#Homebrew 安装">Homebrew 安装</a>
        - <a href="#poppler 安装">poppler 安装</a>
        - <a href="#tesseract 安装">tesseract 安装</a>
        - <a href="#高频词汇分析 安装">高频词汇分析 安装</a>
- <a href="#Change Log">Change Log</a>
- <a href="#常见问题">常见问题</a>

## 项目概述

高频词汇分析是一款开源词汇频率分析软件。主要功能包括：PDF 中文文字提取，文章关键字提取，简单趋势分析，以及输出数据到 excel 文档。
开发语言为 python，使用 tkinter GUI 打造的界面帮助简单参数配置。

<img src="resource/readme/project_overview.png" alt="project overview">

## 界面与功能介绍

当您打开高频词汇分析软件时，以下页面将会被展示：

<img src="resource/readme/main_screen_intro.png" alt="main screen introduction">

软件主页面包括以下几个部分：

- 参数面板：所有可配置的参数都在这个面板上，该面板还包括几个副面板，详情请见<a href="#参数面板及可配置参数">参数面板以及可配置参数</a>。
- 进度面板：进度面板描述了现在正在进行的任务，以及任务的状态，详情请见<a href="#进程面板">进程面板</a>。
- 控制面板：控制面板是所以任务按钮所在的面板，详情请见<a href="#控制面板">控制面板</a>。
- 状态面板：状态面板是反应详细的程序状态以及任务状态的窗口，详情请见<a href="#状态面板">状态面板</a>。
- 版本号：程序的版本号

### 参数面板及可配置参数
参数面板包含以下几个副面板：
- 文件选择
    - 根目录选择
        - （必填项）选择根目录，更多关于<a href="#创建根目录">根目录</a>
    - 索引文件选择
        - （必填项）选择索引文件，更多关于<a href="#索引文件格式">索引文件</a>
    - 附加参数文件选择
        - 选择索引文件，更多关于<a href="#附加参数文件格式">附加参数文件</a>
- pdf处理
    - 处理引擎
        - 一共有两个选项，各代表使用两个不同的库来处理pdf
        - pdftoppm（默认）
        - pdftocairo：可能在大型文件中性能有提升
    - 扫描格式
        - jpeg（推荐，默认）：文件较小，性能平均
        - png：文件较大，性能平均
        - tiff：文件最大，无压缩，还原度高
    - 扫描 DPI
        - DPI 是 Dots Per Inch（每英寸点数）的简称。DPI 越大，图像还原度越高。
        - 300（默认），400，500，600
- ocr优化
    - ocr 优先级
        - 优先速度：使用 <a href="https://github.com/tesseract-ocr/tessdata_fast">`tessdata/fast`</a> 来作为训练模型。该存储库包含Tesseract开源OCR引擎的训练模型的快速整数版本。
        - 平均（默认）：使用 <a href="https://github.com/tesseract-ocr/tessdata">`tessdata/default`</a> 来作为训练模型。该存储库包含Tesseract开源OCR引擎的训练模型的默认版本，支持旧版和LSTM OCR引擎。
        - 优先质量：使用 <a href="https://github.com/tesseract-ocr/tessdata_best">`tessdata/best`</a> 来作为训练模型。该存储库包含Tesseract开源OCR引擎的训练模型的最好版本。
    - ocr 默认语言
        - 默认语言：当无附加参数时使用的识别语言，更多关于<a href="#附加参数文件格式">附加参数</a>
            - 简体中文，繁体中文
- jieba优化
    - 抽取词汇数目
    - 高频词汇抽取器
- 词汇编辑
    - 词性筛选
    - 建议词汇
    - 白名单词汇
    - 黑名单词汇
- 统计分析器
    - 统计分析器
        - 趋势分析器

### 进程面板
进程面板包括两个部分：
- 任务描述
    - 任务描述包括了关于进程大部分信息，包括预计剩余时间（有可能不准确）。
- 任务处理进程
    
以下是一个进程面板的示例：
<img src="resource/readme/progress_demo.png" alt="progress demo">

### 控制面板
控制面板是开始任务的端口，里面包括了所有任务的对应按钮：
1. <a href="#预处理">预处理</a>
2. <a href="#装载数据">装载数据</a>
3. <a href="#抽取词汇">抽取词汇</a>
4. <a href="#统计分析">统计分析</a>
5. <a href="#输出">输出</a>

任务之间是有先后顺序的。当刚开启软件时，有些任务会被禁用，只有完成了其之前的任务才可以开始下一任务。
例如：*统计分析* 是不可以执行的，的直到 *抽取词汇* 执行完成。
同理，如果重新执行了 *装载数据*，在其之后的 *统计分析*，*输出* 都将被禁用。

<img src="resource/readme/action_order.png" alt="action order">

如果在任务处理途中有错误发生，该任务线程会马上退出，一个窗口会弹出并告知用户错误详情。
请详细查看错误报告，并在<a href="#常见问题">常见问题</a>里寻找对应的解决办法，如果还未能解决请<a href="mailto:homeletwei@gmail.com">联系开发者</a>。

<img src="resource/readme/action_error.png" alt="action error">

注意事项：
- 当开始一项任务时，与该任务相关的一些参数面板会被禁用。
- __任务线程一旦开始就不可以手动停止。如果想要强制终止任务，请关闭软件然后重新开始。__

控制面板包括了一些辅助功能：
- <a href="#校对预处理">校对预处理</a>，按下将会打开电脑上的 `根目录/data` 文件夹方便用户校对。
- <a href="#初步检查词汇">初步检查词汇</a>，按下会打开一个界面显示已经被抽取的词汇（可以忽略这步）。

控制面板还包括一些其他功能型的复选框：
- 自动开始下一步骤，选中之后将在完成一个任务后一秒钟自动开始下一个任务。
- 输出统计细节，选中之后将在输出的 excel 文件中包括一些统计细节（拟合系数，RMSE）

### 状态面板
状态面板反应详细的程序状态以及任务状态的窗口，所有的任务信息都会显示在这里，包括 任务信息，错误信息，...

<img src="resource/readme/status_error.png" alt="status error ">

<img src="resource/readme/status_info_1.png" alt="status info 1">

<img src="resource/readme/status_info_2.png" alt="status info 2">

## 分析流程介绍

<img src="resource/readme/work_process.png" alt="work process">

### 创建根目录

如果想要开始分析首先我们需要一个根目录。
请在您喜欢的位置创建一个新的文件夹，并改成您喜欢的名字。

根目录是我们分析过程中必不可少的，在分析过程中根目录里可能会用到的副目录：

- `根目录/resource`：（这个目录是我们需要自己创建的）这里是我们所有要被分析的源文件的所在之地，在索引文件里用到的文件应都在这里。
- `根目录/data`：（这个目录是程序自动给我们创建的）这里是程序预处理完成后所有处理文件都将会被保存在这里。
- `根目录/temp`：（这个目录是程序自动给我们创建的）这里是程序预处理时要用到的pdf扫描文件被保存的地方。（这个文件夹可能会占用很多电脑空间，可以定期删除里面的文件）

### 准备数据

接下来我们需要在我们刚创建好的文件夹里面创建一个子文件夹，并命名为 `resource`。
然后把所有会用到的源文件（分析文件）移动到 `resource` 文件夹下。

### 创建索引

现在我们需要创建两个文件，索引文件 和 附加参数文件。这两个文件格式为.xlsx/.xls（Excel 文件）。
索引文件是用于告诉程序想要分析的数据的具体信息，附加参数文件是用于告诉程序一些附加的参数。

#### 索引文件格式
<table style="width:100%">
  <tr>
    <th>名字</th>
    <th>文件地址</th>
    <th>类别</th>
    <th>排序代码</th>
    <th>开始页码</th>
    <th>结束页码</th>
    <th>附加参数</th>
  </tr>
  <tr>
    <td>中国共产党党章（七大）</td>
    <td>data.pdf</td>
    <td>七大</td>
    <td>7</td>
    <td>487</td>
    <td>504</td>
    <td>CROP=210/280/2300/3050｜LANG=chi_sim</td>
  </tr>
</table>
参数具体含义：

- 名字：数据的名字
- 文件地址：数据所在文件的名字，请加入文件后缀 .docx，.pdf 之类（注意，请确保该文件在 `根目录/resource` 下存在，如果没有请把该文件复制到 `根目录/resource`）
- 类别：这个数据所属于的类别，相同类别的数据将会被归成一类。
- 排序代码：一个数字代表这个数据所属类别的排序代码，相同类别的数据必须拥有相同的排序代码
- 开始页码：一个数字代表数据在 PDF 文件中开始的页码。如果文件格式为.docx（word 文档）这个值将会被忽略。注意这个页码为真实页码，可能与 PDF 中角标页码不符（请确保 开始页码 小于等于 结束页码）。
- 结束页码：一个数字代表数据在 PDF 文件中结束的页码。如果文件格式为.docx（word 文档）这个值将会被忽略。注意这个页码为真实页码，可能与 PDF 中角标页码不符（请确保 结束页码 大于等于 开始页码）。
- 附加参数：对于这个文件的具体附加参数，如果这个参数不为空，附加参数文件的参数会被暂时覆盖。
    - 格式为：CROP=210/280/2300/3050｜LANG=chi_sim，用 `|` 隔开参数，具体关于附加参数，请查看 附加参数文件格式。


#### 附加参数文件格式
<table style="width:100%">
  <tr>
    <th>文件地址</th>
    <th>裁剪参数</th>
    <th>识别语言</th>
  </tr>
  <tr>
    <td>data.pdf</td>
    <td>CROP=210/280/2300/3050</td>
    <td>LANG=chi_sim</td>
  </tr>
</table>
参数具体含义：

- 文件地址：文件的名字，这一项与索引文件里文件地址规则相同。
- 裁剪参数：这一参数的作用是通过裁剪扫描图片的方式，帮助程序过滤掉一些无用的信息。
    - 格式为：`CROP=x/y//height`
<img src="resource/readme/crop_parm_demo.png" alt="crop parm demo" height="150px">     
    - 比如说在某些 PDF 文件里每一页会出现的页眉，页脚，页码，假如这些是一些我们不想要的干扰数据，
<img src="resource/readme/data-300-0149.jpg" alt="crop example" height="700px">
    - 我们可以通过设定一个裁剪参数使这些干扰数据不被识别。
- 识别语言：这一参数的作用是设定一个识别语言，来更好的识别数据。
    - 格式为：`LANG=语言1+语言2`
<img src="resource/readme/lang_parm_demo.png" alt="lang parm demo" height="150px">
    - 目前支持的语言有
        - 简体中文：chi_sim
        - 繁体中文：chi_tra
    - 选择语言时应遵守以下规则以增加识别准确度
        - 尽量准确选择可能出现的语言
        - 尽量排除不会出现的语言来减少干扰
    - 关于 Tesseract-ocr 支持语言请前往：<a href="https://github.com/tesseract-ocr/tessdoc">tesseract doc</a>

### 预处理

### 校对预处理

### 装载数据

### 抽取词汇

### 初步检查词汇*

### 统计分析

### 输出

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

#### python 与 pip 安装

请前往 <a href="https://www.python.org/downloads/">python 官方下载网站</a> 
进行下载，点击下载 python 3.8 或以上的版本（注意要 64bit 版）。下载后双击运行文件，一直点击下一步直到安装结束。

<img src="resource/readme/python_install_success.png" alt="python install success">

接下来我们验证 python 与 pip 是否被正确安装。

首先<a href="#1. 如何打开 终端.app（Terminal.app）">打开 终端.app（Terminal.app）</a>，打开聚焦搜索（同时按下 Command + 空格键），输入 Terminal.app

<img src="resource/readme/terminal_open.png" alt="terminal open">

接下来输入 `python3 -V` 和 `pip3 -V`

```
➜  ~ python3 -V
Python 3.8.3
➜  ~ pip3 -V
pip 20.0.2 from ... (python 3.8)
```

如果返回结果类似于 `Python 3.8.3` 和 `pip 20.0.2` 说明您已经成功安装 Python 3.8.3！

#### Homebrew 安装

在安装 高频词汇分析 之前我们需要安装几个项目依赖库，我们将使用包管理工具 Homebrew 来协助我们安装。
请首先打开<a href="#1. 如何打开 终端.app（Terminal.app）">终端（Terminal.app）</a>且输入以下命令：

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

如果程序提醒 "Press Enter to continue"，请按下回车键。以下是示例结果：

如果程序提醒 "Enter Password"，请输入电脑密码然后按下回车键来继续安装。（注意，密码因为隐私原因，打出来的密码会不可见。这是正常现象，请继续输入。如果密码打错了，可以提前按下回车键即可重新尝试输入。）
```
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
```

#### poppler 安装

接下来请在<a href="#1. 如何打开 终端.app（Terminal.app）">终端（Terminal.app）</a>对话框输入以下命令来安装 `poppler` 库（提供关于 PDF 处理支持）。

`brew install poppler`

以下是示例结果：

```
➜  ~ brew install poppler 
==> Downloading https://homebrew.bintray.com/bottles/poppler-0.88.0.catalina.bot
...
==> Pouring poppler-0.88.0.catalina.bottle.tar.gz
🍺  /usr/local/Cellar/poppler/0.88.0: 459 files, 24.9MB
```

<h4 id="tesseract_install">tesseract 安装</h4>

接下来请在<a href="#1. 如何打开 终端.app（Terminal.app）">终端（Terminal.app）</a>对话框输入以下命令来安装 `tesseract` 库（提供关于光学字符识别（OCR）支持）。

`brew install tesseract`

以下是示例结果：
```
➜  ~ brew install tesseract 
==> Downloading https://homebrew.bintray.com/bottles/tesseract-4.1.1.catalina.bo
...
==> Pouring tesseract-4.1.1.catalina.bottle.tar.gz
==> Caveats
This formula contains only the "eng", "osd", and "snum" language data files.
If you need any other supported languages, run `brew install tesseract-lang`.
==> Summary
🍺  /usr/local/Cellar/tesseract/4.1.1: 65 files, 29.6MB
```

#### 高频词汇分析安装

接下来我们将安装主体程序，前往[发布版本列表](release)来选择安装版本，或者直接下载[推荐版本](release/V 0.1/高频词汇分析_release_0.1.zip?raw=true)。

接下来将下载好的 zip 文件移动到您喜欢的位置（例如，桌面）然后双击解压，并且将解压好的文件夹改成喜欢的名字。

__!! 注意：一旦程序设定完成，将不能改变该文件夹地址以及名字，所以要现在设置完成 !!__

双击打开该文件夹，找到 `install_script.sh` 文件。

现在请在<a href="#1. 如何打开 终端.app（Terminal.app）">终端（Terminal.app）</a>对话框输入 `sh` 并且把 `install_script.sh` 拖入对话框中，然后按下回车键。

<img src="resource/readme/drag_install_script.gif" alt="drag install script">

以下是示例结果：
```
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
```

恭喜您，您已经成功安装了高频词汇分析！

在结束安装之后，会自动弹出一个含有 *高频词汇分析.app* 的窗口，双击 *高频词汇分析.app* 来测试程序运行，
如果运行成功，程序主页面将会展示。

如果没有发现<u>高频词汇分析.app</u>，可能有以下几个原因:
1. 窗口失败弹出，请检查在目录下的 _dist_ 文件夹，
2. 如果在 _dist_ 文件夹还未发现<u>高频词汇分析.app</u>，说明安装失败，请联系开发者来获取更多信息，或者重新尝试上一步。


运行成功之后可以把 *高频词汇分析.app* 文件拖入 程序（Application）文件夹，来快速访问。


## Change Log

`V0.2` 改善 PDF 处理速度，运用 mutiprocessing.

`V0.1` 初版本发布

## 常见问题

#### 1. 如何打开 终端.app（Terminal.app）

<h5>方法1：</h5>
打开聚焦搜索（同时按下 Command + 空格键），输入 终端.app（Terminal.app），按下回车即可打开。

<img src="resource/readme/terminal_open.png" alt="terminal open">

<h5>方法2：</h5>
Application 文件夹并搜索 终端.app（Terminal.app），双击即可打开。


#### 2. 值错误

#### 3. Unable to get Page Count, is poppler installed?

首先<a href="#1. 如何打开 终端.app（Terminal.app）">打开终端（Terminal.app）</a> 输入以下指令：

`brew unlink poppler && brew link poppler`




