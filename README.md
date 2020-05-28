# 高频词汇分析 （hf_word_analysis)

- <a href="#项目概述">项目概述</a>
- <a href="#界面与功能介绍">界面与功能介绍</a>
    - <a href="#参数面板及可配置参数">参数面板及可配置参数</a>
    - <a href="#进程面板">进程面板</a>
    - <a href="#控制面板">控制面板</a>
    - <a href="#状态面板">状态面板</a>
- <a href="#使用教程">使用教程</a>
    - <a href="#创建根目录">创建根目录</a>
    - <a href="#准备数据">准备数据</a>
    - <a href="#创建索引">创建索引</a>
        - <a href="#索引文件格式">索引文件格式</a>
        - <a href="#附加参数文件格式">附加参数文件格式</a>
        - <a href="#裁剪参数用途">裁剪参数用途</a>
    - <a href="#预处理">预处理</a>
    - <a href="#校对预处理">校对预处理</a>
    - <a href="#装载数据">装载数据</a>
    - <a href="#抽取词汇">抽取词汇</a>
    - <a href="#初步检查词汇">初步检查词汇</a>
    - <a href="#统计分析">统计分析</a>
    - <a href="#输出">输出</a>
- <a href="#如何安装">如何安装</a>
    - <a href="#macos">MacOs</a>
        - <a href="#python与pip安装">python 与 pip 安装</a>
        - <a href="#homebrew安装">Homebrew 安装</a>
        - <a href="#poppler安装">poppler 安装</a>
        - <a href="#tesseract安装">tesseract 安装</a>
        - <a href="#高频词汇分析安装">高频词汇分析 安装</a>
- <a href="#changelog">Change Log</a>
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

## 使用教程

<img src="resource/readme/work_process.png" alt="work process">

想要使用高频词汇分析，应遵守以下执行顺序:

<a href="#创建根目录">创建根目录</a> ➡️ <a href="准备数据#">准备数据</a> ➡️ <a href="#创建索引">创建索引</a> ➡️ <a href="#预处理">预处理</a> ➡️ <a href="#校对预处理">校对预处理</a> ➡️ <a href="#装载数据">装载数据</a> ➡️ <a href="#抽取词汇">抽取词汇</a> ➡️ <a href="#初步检查词汇">初步检查词汇</a> ➡️ <a href="#统计分析">统计分析</a> ➡️ <a href="#输出">输出</a>

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
索引文件是用于告诉程序想要分析的数据的具体信息，包括数据的具体位置以及类别。

附加参数文件是用于声明对与每个文件的额外参数，包括裁减参数与识别语言。

_注意：附加参数文件是用于帮助更好的分析您的数据，如果没有需要，这个文件是可以被省略的。_

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

[索引文件模板](resource/template/index.xlsx)

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

[附加参数文件模板](resource/template/additioanl_pram.xlsx)

参数具体含义：

- 文件地址：文件的名字，这一项与索引文件里文件地址规则相同。
- 裁剪参数：这一参数的作用是通过裁剪扫描图片的方式，帮助程序过滤掉一些无用的信息。
    - 关于裁减参数用途请参考：<a href="#裁剪参数用途">裁剪参数用途</a>
    - 格式为：`CROP=x/y//height`
    
<img src="resource/readme/crop_parm_demo.png" alt="crop parm demo" height="150px" width="450px"> 

- 识别语言：这一参数的作用是设定一个识别语言，来更好的识别数据。
    - 目前支持的语言有
        - 简体中文：chi_sim
        - 繁体中文：chi_tra
    - 选择语言时应遵守以下规则以增加识别准确度
        - 尽量准确选择可能出现的语言
        - 尽量排除不会出现的语言来减少干扰
    - 关于 Tesseract-ocr 支持语言请前往：<a href="https://github.com/tesseract-ocr/tessdoc">tesseract doc</a>
    - 格式为：`LANG=语言1+语言2`
    
<img src="resource/readme/lang_parm_demo.png" alt="lang parm demo" height="150px" width="450px">

### 预处理
当您已经完成了前三步，您已经准备好开始进行预处理了。

请打开 _高频词汇分析.app_，首先我们要做的是将刚刚准备好的 *根目录*，*索引文件* 以及 *附加参数文件*（附加参数文件可以省略），输入到软件中。

在<a href="#参数面板">参数面板</a>上（位于主界面上半部分），找到 *文件选择* 然后单击 *选择 根目录*，然后在 *访达（Finder）* 对话框中选择您创建的根目录。

接下来同样在 *文件选择* 中单击 *选择 索引文件*，然后在 *访达（Finder）* 对话框中选择您创建的索引文件。

最后同样在 *文件选择* 中单击 *选择 附加参数文件*，然后在 *访达（Finder）* 对话框中选择您创建的索引文件。

__小技巧：如果选择错误可以重新点击选择再次选择。如果想要删除选择的文件/目录，可以点击位于右侧的 'x' 按钮即可删除。
如果想要查看选择的具体目录，可以双击目录即可查看。__

在选择完成文件后，我们就可以开始进行 *预处理*。请在<a href="#控制面板">控制面板</a>上（位于主界面下半部分），找到 *预处理* 按钮，单击即可开始预处理任务。

注意事项：
- 预处理任务可能会花费很久时间，如果想要提升预处理速度，请参考:<a href="#提升预处理速度">提升预处理速度</a>
- 当您已经进行过预处理了，并且不想重新分析一边数据（会覆盖之前预处理的结果），预处理任务是可以跳过的，那么请直接开始<a href="#装载数据">装载数据</a>。
- 预处理所产生的的扫描文件（.png, .jpeg, .tiff）会被保存在 `根目录/temp`，使用久了可能会占用很多内存，请定期清理。

#### 关于预处理

预处理的任务是帮助我们统一归纳数据，他会把所有的数据文件转化为 DATA 文件并保存在 `根目录/data` 下以便以后校对与分析。

<img src="resource/readme/preprocess_process.png" alt="preprocess process">

首先预处理进程会读取 *索引文件* 和 *附加参数文件* 并且分配任务。word 文档，txt文件等文本文档会被直接输出成 DATA 文件。
接下来的任务就是帮助我们把正常无法提取文字的扫描版 PDF 文件的部分，利用 OCR（Optical Character Recognition，光学字符识别）技术提取文字并转化为 DATA 文件。

但是请注意，OCR 技术 无法 100% 准确的识别文字（平均准确度在 80%～90%）。
当然有一些设置可以帮助 OCR 来提升识别文字的准确度，比如用更高的 DPI 扫描 pdf 文件，用 tiff 这种无损无压缩的图像保存格式来保存扫描文档（更多请见<a href="#提升预处理速度">提升预处理速度</a>，<a href="#提升预处理质量">提升预处理质量</a>）。
但是这些方法都无一例外存在弊端，会导致处理时间的曾长或者消耗更多电脑内存。所以*人工校对*是确保准确度的另一办法（请参考下一步 <a href="#校对预处理">校对预处理</a>）。

### 校对预处理

当预处理完成时，会在 `根目录/data` 文件夹里产生一系列的  DATA 文件。请先阅读 <a href="#关于预处理">关于预处理</a> 来了解为什么要校对预处理。

以下是一个示例 DATA 文件：
```
# 可信度 | 行内容 （请校对识别内容，特别注意带有 ？ 的行）
#============== 页码: 33, 平均可信度: 89.68 ==============
#文件地址: /home/homelet/Desktop/数据/temp/data-300-0033.png
  90.57 | 中国共产党宣言
? 84.89 | 《一九二O〇年十一月)
  92.08 | 亲爱的同志们!这个宣言是中国共产党在去年十一月间决定的。这宣言的
  94.31 | 内容不过是关于共产主义原则的一部分，因此没有向外发表，不过以此为收纳
  93.34 | 党员之标准。这宣言之中文原稿不能在此地找到，所以兄弟把他从英文稿翻译
  94.06 | 出来。决定这宣言之时期既然有一年多了，当然到现在须要有修改和添补的地
  91.33 | 方。我很希望诸位同志把这个宣言仔细研究一普，因为每一个共产主义者都得
  92.19 | 要注意这种重要的文件一一共产党宣言。并且会提出远东人民会议[2]中国代
  93.64 | 表团中之共产主义者组讨论。讨论的结果，将要供中国共产党的参考和采纳。
? 62.48 | Chang[3】]
  95.50 | 一九二一年十二月十日
? 83.38 | 1，共产主义者的理想
  93.04 | A.对于经济方面的见解共产主义者主张将生产工具一一机器工厂，原料，
  90.74 | 土地，交通机关等一一收归社会共有，社会共用。要是生产工具收归共有共用
...
#=================总体平均可信度 : 89.68==================
```
每一页 PDF 文档都对应着DATA 文件中的一个段落。每个段落的第一行展示了 *页码* 以及这一页的 *平均可信度*。紧接着第二行展示了这个行对应的文件地址。接下来的 n 行就是扫描内容（n 为这个页一共有多少行）。

每一行内容的格式为：
```
 行可信度 | 行内容
```
如果这一行的 *行可信度* 低于这一页的 *平均可信度*，在这一行的最前面将会标注 `?`。

**__要点：当我们进行人工校对时请重点注意前面带有 `?` 的行。__**

如果的行的开头符号为 `#`，这一行将成为注释行（程序不会识别）。例如：
```
#这是一行注释行，程序将不会识别这一行的内容。
```

### 装载数据

当您完成了预处理，或者之前已经进行过预处理。您现在已经可进行装载数据了。

请在<a href="#控制面板">控制面板</a>上（位于主界面下半部分），找到 *装载数据* 按钮，单击即可开始装载数据任务。

装载数据的目的是程序用来读取预处理过的 DATA 数据的。首先他会读取索引文件，然后找到 `根目录/data` 文件夹并读取所有索引文件里提及到的 DATA 文件。

### 抽取词汇

当数据已经装载完成，*抽取词汇* 按钮就会被激活，

### 初步检查词汇*

### 统计分析

### 输出

## 性能提升技巧

### 裁剪参数用途
比如说在某些 PDF 文件里每一页会出现的页眉，页脚，页码，假如这些是一些我们不想要的干扰数据，

<img src="resource/readme/data-300-0149.jpg" alt="crop example" height="700px">

我们可以通过设定一个裁剪参数使这些干扰数据不被识别。

### 提升预处理速度

### 提升预处理质量

### 提升词汇抽取准确率

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

### macos

#### python与pip安装

请前往 <a href="https://www.python.org/downloads/">python 官方下载网站</a> 
进行下载，点击下载 python 3.8 或以上的版本（注意要 64bit 版）。下载后双击运行文件，一直点击下一步直到安装结束。

<img src="resource/readme/python_install_success.png" alt="python install success">

接下来我们验证 python 与 pip 是否被正确安装。

首先<a href="#如何打开终端appTerminalapp">打开 终端.app（Terminal.app）</a>，打开聚焦搜索（同时按下 Command + 空格键），输入 Terminal.app

<img src="resource/readme/terminal_open.png" alt="terminal open">

接下来输入 `python3 -V` 并按回车键

```
➜  ~ python3 -V
Python 3.8.3
```

接下来输入 `pip3 -V` 并按回车键

```
➜  ~ pip3 -V
pip 20.0.2 from ... (python 3.8)
```

如果返回结果类似于 `Python 3.8.3` 和 `pip 20.0.2` 说明您已经成功安装 Python 3.8.3！

#### homebrew安装

在安装 高频词汇分析 之前我们需要安装几个项目依赖库，我们将使用包管理工具 Homebrew 来协助我们安装。
请首先打开<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>且输入以下命令并按回车键：

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

#### git安装

接下来我们安装 git 我们需要用 git 来配置一些文件。请在<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>对话框输入以下命令并按回车键来安装 git.

`brew install git`

#### 配置homebrew

因为 Homebrew 的服务器在国外，所以国内下载可能会有些慢，接下来我们把 homebrew 的源改成国内的源，这样将会提升下载速度。

这里我们使用 清华大学 提供的源。

请在<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>对话框输入以下命令并按回车键，注意请一行一行输入，等前一行执行结束后在输入下一行。

`git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git`

`git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git`

`git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git`

`git -C "$(brew --repo homebrew/cask-fonts)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-fonts.git`

`git -C "$(brew --repo homebrew/cask-drivers)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-drivers.git`

`brew update`

#### poppler安装

接下来请在<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>对话框输入以下命令并按回车键来安装 `poppler` 库（提供关于 PDF 处理支持）。

`brew install poppler`

以下是示例结果：

```
➜  ~ brew install poppler 
==> Downloading https://homebrew.bintray.com/bottles/poppler-0.88.0.catalina.bot
...
==> Pouring poppler-0.88.0.catalina.bottle.tar.gz
🍺  /usr/local/Cellar/poppler/0.88.0: 459 files, 24.9MB
```

#### tesseract安装

接下来请在<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>对话框输入以下命令并按回车键来安装 `tesseract` 库（提供关于光学字符识别（OCR）支持）。

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

接下来我们将安装主体程序，前往[发布版本列表](release)来选择安装版本，或者直接下载[推荐版本](https://github.com/HomeletW/high-frequency-words-analysis/blob/master/release/V%200.2.1/%E9%AB%98%E9%A2%91%E8%AF%8D%E6%B1%87%E5%88%86%E6%9E%90_release_0.2.1.zip?raw=true)。

接下来将下载好的 zip 文件移动到您喜欢的位置（例如，桌面）然后双击解压，并且将解压好的文件夹改成喜欢的名字。

__!! 注意：一旦程序设定完成，将不能改变该文件夹地址以及名字，所以要现在设置完成 !!__

双击打开该文件夹，找到 `install_script.sh` 文件。

现在请在<a href="#如何打开终端appTerminalapp">终端（Terminal.app）</a>对话框输入 `sh` 并且把 `install_script.sh` 拖入对话框中，然后按下回车键。

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

## 常见问题

### 如何打开终端.app（Terminal.app）

<h5>方法1：</h5>
打开聚焦搜索（同时按下 Command + 空格键），输入 终端.app（Terminal.app），按下回车即可打开。

<img src="resource/readme/terminal_open.png" alt="terminal open">
<h5>方法2：</h5>
Application 文件夹并搜索 终端.app（Terminal.app），双击即可打开。

### 值错误

### Unable to get Page Count, is poppler installed?

首先<a href="#如何打开终端appTerminalapp">打开终端（Terminal.app）</a> 输入以下指令：

`brew unlink poppler && brew link poppler`

## Change log

`V0.2` 改善 PDF 处理速度，运用 mutiprocessing，修复编码问题。

`V0.1` 初版本发布




