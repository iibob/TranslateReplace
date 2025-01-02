# 翻译助手
![000](https://github.com/user-attachments/assets/48a75c96-656c-44be-af3f-3e28fef25564)

<br>

## 功能：

自动替换选中的文本为译文。

![001](https://github.com/user-attachments/assets/7de43fa4-aa07-4edf-8157-11e486de8f17)

<br>

## 注意事项：

- 为实现译文替换原文，需在文本编辑区域使用，比如记事本、聊天输入框等。
- 若选中网页中的文本执行翻译，无替换效果，但会将译文写入剪贴板。
- 程序基于系统剪贴板获取选中的文本和替换成译文，使用过程会将原文和译文写入到剪贴板历史。
- 程序依赖百度翻译服务，需要注册服务后才能使用。注意别泄露 ID 和密钥，滥用超额会产生费用。
- 程序使用 Python 开发，所以打包后的体积较大。
<br>

## 帮助：
### 获取 APP ID 和密钥
请前往 [百度翻译开放平台](https://fanyi-api.baidu.com/product/11) 获取。

操作步骤参考：[点击查看](https://bobtranslate.com/service/translate/baidu.html)

### 操作步骤
1. 打开软件，点击 [设置] 配置百度翻译
2. 设置自己喜欢的快捷键
3. 点击 [开启]
4. 鼠标选中需要翻译的文本，按下快捷键
5. 完成

![002](https://github.com/user-attachments/assets/8f8deb8c-2839-4355-a894-7bc12d41f070)

<br>

## 更新日志：
<details><summary>点击打开</summary>

**2024年12月31日&nbsp;&nbsp;&nbsp;&nbsp;v0.2.2**
- 使用更加现代化的 GUI 工具 wxPython 重构了界面

**2024年12月16日&nbsp;&nbsp;&nbsp;&nbsp;v0.1.0**
- 初代版本发布
- 使用 tkinter 构建

</details>
<br>
