# 测试文件上传系统使用说明

## 目录

[TOC]

## 1. 总览

​	本 webApp 旨在为用户提供一个方便的平台，用于上传测试生成的数据文件，通过我们预制好的分析脚本（包括 Python 和 Perl）进行分析，并将分析结果作为 Excel 文件放在页面上供用户下载

​	在浏览器地址栏（WindowsXP系统建议使用360极速浏览器）输入局域网网址**http://192.168.2.143**即可进入测试文件上传系统主页面：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019172845.png" alt="QQ截图20231019172845" style="zoom:150%;" />

​	鼠标放在页面最左侧就会出现左侧边栏，这个边栏提供了前往主页面、管理我们分析数据脚本、显示此说明文档，系统更新（专供开发人员后期新增功能的使用，用于拉取最新的本地仓库代码）的选项：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019173406.png" alt="QQ截图20231019173406" style="zoom:150%;" />

​	鼠标放在页面最右侧就会出现右侧边栏，这个边栏可以看到我们上传过的待分析的数据文件、处理数据的日志、以及经过分析脚本所生成的excel文件，它们会按照日期进行分类，我们随时可以点击超链接进行下载：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019180019.png" alt="QQ截图20231019180019" style="zoom:150%;" />

## 2. 主要功能

### 2.1 上传待分析的数据文件（.txt）

#### 2.1.1 **通过选择的方式上传**

##### 2.1.1.1 **通过选择单个或多个文件的方式上传数据**

​	我们可以单击第一个“选择单个或多个文件”来上传我们的数据：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019180432.png" alt="QQ截图20231019180432" style="zoom:150%;" />

​	然后选择我们需要分析的数据文件：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019180633.png" alt="QQ截图20231019180633" style="zoom:150%;" />

​	此外，我们也可以事先打开数据文件所在的文件夹，然后选中文件后通过拖拽的方式直接进行预上传：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019180830.png" alt="QQ截图20231019180830" style="zoom:150%;" />

> tips：考虑到特殊情况，如果用户要同时上传不同文件夹里的不同文件，比如我们要同时上传A文件夹里的“a.txt”和B文件夹里的“b1.txt”、“b2.txt”，我们就可以使用到这里面的“+”按钮来解决这种情况：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019204902.png" alt="QQ截图20231019204902" style="zoom:150%;" />

​	然后选择我们的分析脚本：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019183611.png" alt="QQ截图20231019183611" style="zoom:150%;" />

​	最后，点击旁边的上传按钮：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019183800.png" alt="QQ截图20231019183800" style="zoom:150%;" />

​	脚本运行成功之后，页面上会罗列出一系列信息：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019184320.png" alt="QQ截图20231019184320" style="zoom:150%;" />

​	预览生成的excel文件：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019184714.png" alt="QQ截图20231019184714" style="zoom:150%;" />

​	至此，我们根据选择上传单个或多个文件的分析数据流程已完毕

>  **特别提醒**：这个上传文件的方式同时支持上传**电脑本地**的文件和**网盘中**的文件，但是由于浏览器隐私政策的限制，这种方式在使用分析脚本后生成的Excel文件**不会生成到源路径之中**，我们需要自行点击超链接进行下载

##### 2.1.1.2 **通过选择整个文件夹的方式上传数据**

​	除了第一种方法外，我们还可以单击第二个“选择整个文件夹中的所有文件”来上传我们的数据（假设文件夹中有4个txt文件，这里我们使用即将被perl脚本分析的数据）：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019185334.png" alt="QQ截图20231019185334" style="zoom:150%;" />

​	然后选择对应的文件夹，这里会上传文件夹里的所有文件

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20230926154107.png" alt="QQ截图20230926154107" style="zoom:150%;" />

​	此外，我们同样也可以事先打开数据文件所在的文件夹，然后选中文件夹后通过拖拽的方式直接进行预上传：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019204300.png" alt="QQ截图20231019204300" style="zoom:150%;" />

> tips：同上面一样，考虑到特殊情况，如果用户要同时上传不同文件夹，比如我们要同时上传A文件夹和B文件夹（都代指里面的所有文件），我们就可以使用到这里面的“+”按钮来解决这种情况：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019204652.png" alt="QQ截图20231019204652" style="zoom:150%;" />

然后选择我们的分析脚本：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019205841.png" alt="QQ截图20231019205841" style="zoom:150%;" />

​	最后，点击旁边的上传按钮：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019205945.png" alt="QQ截图20231019205945" style="zoom:150%;" />

脚本运行成功之后，页面上会罗列出一系列信息：

​	<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019211012.png" alt="QQ截图20231019211012" style="zoom:150%;" />

​	预览生成的excel文件：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019211110.png" alt="QQ截图20231019211110" style="zoom:150%;" />

​	至此，我们根据选择上传单个或多个文件夹的分析数据流程已完毕

> **特别提醒**：这个上传文件的方式同时支持上传**电脑本地**的文件和**网盘中**的文件，但是由于浏览器隐私政策的限制，这种方式在使用分析脚本后生成的Excel文件**不会生成到源路径之中**，我们需要自行点击超链接进行下载

#### 2.1.2 **通过输入的方式上传**

​	除了前面两种提到的方法外，我们可以直接输入我们**数据文件**在网盘（fileserver）中的*路径*来上传文件：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019212049.png" alt="QQ截图20231019212049" style="zoom:150%;" />

​	脚本运行成功之后，页面上会罗列出一系列信息，都是和上面的差不多：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231019212328.png" alt="QQ截图20231019212328" style="zoom:150%;" />

​	**特别注意：以路径方式上传网盘数据文件，生成的excel文件会直接存放在数据所对应的网盘路径中，不需要进行额外操作，所以更推荐这种方式来进行数据文件分析，当然，这些文件依然可以在网页的主页面以及上传文件历史中随时找到**

### 2.2  左侧边栏功能介绍

#### 2.2.1 前往主页

​	我们可以把鼠标放在页面左边来显示左边栏，在弹出的边栏里点击“前往主页”选项，类似于浏览器的刷新按钮

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021165704.png" alt="微信截图_20231021165704" style="zoom:150%;" />

#### 2.2.2 管理分析脚本

​	我们可以把鼠标放在页面左边来显示左边栏，在弹出的边栏点击“管理分析脚本”选项。

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021172029.png" alt="微信截图_20231021172029" style="zoom:150%;" />

##### **上传脚本操作**

如果我现在需要上传**a.py**和**b.pl**这两个脚本来让页面支持调用，具体操作流程如下：

  * 点击“选择文件”来预上传我们的新脚本：

​	<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021173435.png" alt="微信截图_20231021173435" style="zoom:150%;" />

> 这里也可以像上面一样将我们的脚本拖进来
>
> <img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021174314.png" alt="微信截图_20231021174314" style="zoom:150%;" />

  * 然后点击“保存更改”按钮

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021173738.png" alt="微信截图_20231021173738" style="zoom:150%;" />

* 随后就发现可以在页面中选择我们刚刚上传的脚本了

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231021174603.png" alt="QQ截图20231021174603" style="zoom:150%;" />

##### **删除脚本操作**

如果我现在需要删除在页面显示的**a.py**和**b.pl**这两个脚本，具体操作流程如下：

* 点击目标脚本旁边的“移除脚本”来删除

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021194717.png" alt="微信截图_20231021194717" style="zoom:150%;" />

* 在弹出的确认框中选择“确定”
* 随后在页面中看到我们删除脚本操作已经生效

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231021194954.png" alt="QQ截图20231021194954" style="zoom:150%;" />

> 提示：由于脚本直接放在了APP的特定文件夹里，所有访问APP的设备都会共享这个文件夹里的脚本，所以任何设备对脚本的管理都会影响其他设备的访问效果，为了避免误删操作，请谨慎使用此功能，后续可能会加入类似鉴权或管理权限机制，敬请期待！

#### 2.2.3 显示说明文档

​	我们可以点击侧边栏中的“显示说明文档”选项来弹出我们测试文件上传系统的文档介绍，并且这里也供给了下载文档和放大缩小文档等功能

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021195812.png" alt="微信截图_20231021195812" style="zoom:150%;" />

#### 2.2.4 关于页面

​	点击左侧边栏中的“关于”条目可以展示系统的关于信息以及版本更新信息：

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\QQ截图20231027100116.png" alt="QQ截图20231027100116" style="zoom:150%;" />

#### 2.2.5 系统更新

​	这个功能主要是开放给开发人员使用的，因为我们的APP运行在ubuntu server的docker环境中，docker环境和我们现在开发的windows环境会有些许不同，为了能让我们在windows的更改能够直接作用在docker中，省去打包镜像所浪费的时间，我们制作了这个功能，项目的源代码仓库路径为：*Z:\misc\testing\ATE\K2\zqchen\Program\boya_upload_test_file_sys*

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021201001.png" alt="微信截图_20231021201001" style="zoom:150%;" />

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021201206.png" alt="微信截图_20231021201206" style="zoom:150%;" />



### 2.3 右侧边栏功能介绍

#### 2.3.1 上传文件历史

​	把鼠标放在页面右侧，右侧边栏就会出现，这个边栏主要是按时间降序分类了上传的数据文件、生成的Excel以及记录控制台的log文件，不管我们是通过选择上传的文件，还是通过路径上传的网盘文件，上面提及的文件我们都可以通过这个超链接进行下载。

>  这个文件历史也是有清理机制的：
>
>  ​	① 每*10*分钟只保留最新的*15*个文件上传记录
>
>  ​	② 每天凌晨*4*点删除所有的文件上传记录

<img src="Z:\misc\testing\ATE\K2\zqchen\Program\images\微信截图_20231021211606.png" alt="微信截图_20231021211606" style="zoom:150%;" />
