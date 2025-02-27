import wx
import os
import json
import pyperclip
import random
from hashlib import md5
import requests
import webbrowser
import math
import shutil
import keyboard
from time import sleep
from hotkey_manager import HotkeyManager


def init_config_file():
    project_dir = os.getcwd()

    items = os.listdir(project_dir)
    folders = []
    for item in items:
        item_path = os.path.join(project_dir, item)
        if os.path.isdir(item_path):
            folders.append(item)

    def create_data_dir(path):
        if not os.path.exists(path):
            os.mkdir(path)  # 创建目录

    data_dir_path = os.path.join(project_dir, "data")
    target_dir_path = os.path.join(project_dir, "_internal")

    if folders and "_internal" in folders:      # 程序已打包
        if 'data' in folders:
            # 首次打开程序，准备移动 data 目录
            if os.path.exists(data_dir_path) and os.path.exists(target_dir_path):
                shutil.move(data_dir_path, target_dir_path)
        else:
            data_dir_path = os.path.join(target_dir_path, "data")
            create_data_dir(data_dir_path)

        file_directory = r"_internal\data"

    else:
        if 'data' not in folders:
            create_data_dir(data_dir_path)

        file_directory = "data"

    icon_image = f"{file_directory}\\icon.png"
    sponsor_image = f"{file_directory}\\sponsor.data"
    dev_image = f"{file_directory}\\dev.data"
    config_file = f"{file_directory}\\config.json"

    return icon_image, sponsor_image, dev_image, config_file


# 打包程序后，修改 app.exe 的文件名为程序名+版本号
version = "v0.2.6"
panel_size = (400, 240)
panel_add_settings_size = (400, 608)
about_size = (550, 775)
custom_line_colour = "#d2d2d2"
about = f"{version}  ·  帮助  ·  反馈  ·  赞助"
about_title_text = f"翻译助手 {version}"
about_developer = "iibob"
about_email = 'iibobapp@gmail.com'
third_party_library = "wxPython、keyboard、pynput、pyperclip、requests"
help_url = "https://www.yuque.com/bo_o/box/pma7zu#PVjrc"
project_url = "https://github.com/iibob/TranslateReplace"
changelog_url = "https://www.yuque.com/bo_o/box/pma7zu#AGCCR"
icon_image, sponsor_image, dev_image, config_file = init_config_file()


class Config:
    @staticmethod
    def load_config():
        if not os.path.exists(config_file):
            default_config = {
                "app_id": "",
                "secret_key": "",
                "shortcut": "ctrl shift f",
                "auto_start": False,
                "language": 0
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

        with open(config_file, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_config(config):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)


class TranslatorFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="翻译助手", size=panel_size, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        # 设置窗口图标
        if os.path.exists(icon_image):
            icon = wx.Icon(icon_image, wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon)

        # 语言代码映射
        self.lang_codes = {
            0: "auto",
            1: "zh",
            2: "cht",
            3: "en",
            4: "jp",
            5: "kor",
            6: "fra",
            7: "spa",
            8: "th",
            9: "ara",
            10: "ru",
            11: "pt",
            12: "de",
            13: "it",
            14: "el",
            15: "nl",
            16: "pl",
            17: "bul",
            18: "est",
            19: "dan",
            20: "fin",
            21: "cs",
            22: "rom",
            23: "slo",
            24: "swe",
            25: "hu",
            26: "vie"
        }

        # 加载配置
        self.config = Config.load_config()
        self.is_active = False

        # 初始化热键管理器
        self.hotkey_manager = HotkeyManager(self.perform_translation)
        self.hotkey_manager.hotkey = self.config["shortcut"].split(' ')

        # 创建主面板
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 第一栏：按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.start_btn = wx.Button(self.panel, label="开 启", size=(-1, 60))
        self.settings_btn = wx.Button(self.panel, label="设置", size=(60, 60))
        button_sizer.Add(self.start_btn, 1, wx.ALL | wx.EXPAND, 5)
        button_sizer.Add(self.settings_btn, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.AddSpacer(15)
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        main_sizer.AddSpacer(5)

        # 第二栏：选项
        option_box = wx.StaticBox(self.panel)
        option_box_sizer = wx.StaticBoxSizer(option_box, wx.HORIZONTAL)
        self.auto_start = wx.CheckBox(self.panel, label="自动开启")
        self.auto_start.SetValue(self.config.get("auto_start", False))
        self.lang_choice_text = wx.StaticText(self.panel, label="译文语言:")
        self.lang_choice = wx.Choice(self.panel, choices=["自动检测", "中文", "繁体中文", "英语", "日语", "韩语", "法语", "西班牙语", "泰语", "阿拉伯语", "俄语", "葡萄牙语", "德语", "意大利语", "希腊语", "荷兰语", "波兰语", "保加利亚语", "爱沙尼亚语", "丹麦语", "芬兰语", "捷克语", "罗马尼亚语", "斯洛文尼亚语", "瑞典语", "匈牙利语", "越南语"])
        self.lang_choice.SetSelection(self.config.get("language", 0))
        option_box_sizer.Add(self.lang_choice_text,  0, wx.ALIGN_CENTER | wx.LEFT, 11)
        option_box_sizer.Add(self.lang_choice, 0, wx.ALIGN_CENTER | wx.LEFT, 8)
        option_box_sizer.Add(wx.StaticText(self.panel, label=""), 1, wx.Top | wx.BOTTOM, 30)
        option_box_sizer.Add(self.auto_start, 0, wx.ALIGN_CENTER | wx.RIGHT, 3)
        main_sizer.Add(option_box_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        main_sizer.AddSpacer(10)

        # 第三栏：设置区域
        self.settings_panel = wx.Panel(self.panel)
        settings_sizer = wx.BoxSizer(wx.VERTICAL)

        # 百度翻译设置
        baidu_box = wx.StaticBox(self.settings_panel, label="百度翻译")
        baidu_sizer = wx.StaticBoxSizer(baidu_box, wx.VERTICAL)

        # 输入框
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        input_sizer.AddSpacer(2)
        input_sizer.Add(wx.StaticText(self.settings_panel, label="APP ID:"), 0, wx.LEFT, 5)
        input_sizer.AddSpacer(2)
        self.app_id = wx.TextCtrl(self.settings_panel)
        self.app_id.SetValue(self.config["app_id"])
        input_sizer.Add(self.app_id, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        input_sizer.AddSpacer(5)
        input_sizer.Add(wx.StaticText(self.settings_panel, label="密钥:"), 0, wx.LEFT, 5)
        input_sizer.AddSpacer(2)
        self.secret_key = wx.TextCtrl(self.settings_panel)
        self.secret_key.SetValue(self.config["secret_key"])
        input_sizer.Add(self.secret_key, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # 按钮
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        help_btn = wx.Button(self.settings_panel, label="帮 助", size=(-1, 35))
        baidu_save_btn = wx.Button(self.settings_panel, label="保 存", size=(-1, 35))
        button_sizer.Add(help_btn, 1, wx.EXPAND | wx.RIGHT, 5)
        button_sizer.Add(baidu_save_btn, 1, wx.EXPAND | wx.LEFT, 5)

        baidu_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        baidu_sizer.AddSpacer(8)
        baidu_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 9)
        baidu_sizer.AddSpacer(18)

        # 快捷键设置
        shortcut_box = wx.StaticBox(self.settings_panel, label="快捷键")
        shortcut_sizer = wx.StaticBoxSizer(shortcut_box, wx.VERTICAL)

        # 修饰键和输入框
        modifier_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrl_cb = wx.CheckBox(self.settings_panel, label="Ctrl")
        self.shift_cb = wx.CheckBox(self.settings_panel, label="Shift")
        self.alt_cb = wx.CheckBox(self.settings_panel, label="Alt")
        self.key_input = wx.TextCtrl(self.settings_panel, size=(40, -1), style=wx.TE_CENTRE)

        # 创建容器 包装修饰键和输入框
        modifier_container = wx.BoxSizer(wx.HORIZONTAL)
        modifier_container.Add(self.ctrl_cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        modifier_container.AddSpacer(5)
        modifier_container.Add(self.shift_cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        modifier_container.AddSpacer(5)
        modifier_container.Add(self.alt_cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        modifier_container.AddSpacer(8)
        modifier_container.Add(self.key_input, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        modifier_sizer.Add(modifier_container, 0, wx.EXPAND)

        # 保存按钮
        shortcut_save_btn = wx.Button(self.settings_panel, label="保 存", size=(90, 35))

        # 设置已保存的快捷键
        saved_shortcut = self.config["shortcut"].lower()
        self.ctrl_cb.SetValue("ctrl" in saved_shortcut)
        self.shift_cb.SetValue("shift" in saved_shortcut)
        self.alt_cb.SetValue("alt" in saved_shortcut)
        key = saved_shortcut.split()[-1]
        if key.isalpha():
            key = key.upper()
        self.key_input.SetValue(key)

        shortcut_sizer.AddSpacer(3)
        shortcut_sizer.Add(modifier_sizer, 0, wx.ALIGN_CENTER | wx.LEFT, 5)
        shortcut_sizer.AddSpacer(8)
        shortcut_sizer.Add(shortcut_save_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 9)
        shortcut_sizer.AddSpacer(18)

        settings_sizer.Add(baidu_sizer, 0, wx.EXPAND | wx.ALL, 5)
        settings_sizer.AddSpacer(10)
        settings_sizer.Add(shortcut_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.settings_panel.SetSizer(settings_sizer)

        main_sizer.Add(self.settings_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.settings_panel.Hide()

        # 第四栏：版本信息
        version_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.version_text = wx.StaticText(self.panel, label=about)
        self.version_text.SetForegroundColour(wx.Colour("#909090"))
        self.version_text.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        # 创建消息文本
        self.message_text = wx.StaticText(self.panel, label="")
        self.message_text.SetForegroundColour(wx.Colour(255, 0, 0))
        self.message_text.Hide()

        version_sizer.Add(self.version_text, 0)
        version_sizer.Add(self.message_text, 0)

        main_sizer.Add(version_sizer, 0, wx.ALIGN_CENTER | wx.TOP, 5)

        self.panel.SetSizer(main_sizer)
        self.Centre()

        # 绑定事件
        self.start_btn.Bind(wx.EVT_BUTTON, self.toggle_active)
        self.settings_btn.Bind(wx.EVT_BUTTON, self.toggle_settings)
        self.lang_choice.Bind(wx.EVT_CHOICE, self.on_lang_choice)
        baidu_save_btn.Bind(wx.EVT_BUTTON, self.save_baidu_settings)
        shortcut_save_btn.Bind(wx.EVT_BUTTON, self.save_shortcut)
        help_btn.Bind(wx.EVT_BUTTON, lambda evt: webbrowser.open(help_url))
        self.version_text.Bind(wx.EVT_LEFT_DOWN, self.about_click)
        self.auto_start.Bind(wx.EVT_CHECKBOX, self.on_auto_start)
        self.key_input.Bind(wx.EVT_CHAR, self.on_key_char)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 初始化消息显示相关的属性
        self.message_timer = None

        # 根据配置文件自动激活程序
        if self.config["auto_start"]:
            self.toggle_active(None)

    def toggle_settings(self, event):
        if self.settings_panel.IsShown():
            self.settings_panel.Hide()
            self.settings_btn.SetLabel("设置")
            self.SetSize(panel_size)
        else:
            self.settings_panel.Show()
            self.settings_btn.SetLabel("隐藏")
            self.SetSize(panel_add_settings_size)
        self.panel.Layout()

    def on_lang_choice(self, event):
        index = self.lang_choice.GetSelection()
        self.config["language"] = index
        Config.save_config(self.config)

    def save_baidu_settings(self, event):
        app_id = self.app_id.GetValue().strip()
        secret_key = self.secret_key.GetValue().strip()

        if not app_id or not secret_key:
            self.show_message("APP ID 和 密钥 不能为空", 5000)
            return

        self.config["app_id"] = app_id
        self.config["secret_key"] = secret_key
        Config.save_config(self.config)
        self.show_message("保存成功")

    def save_shortcut(self, event):
        key = self.key_input.GetValue().strip()

        for char in key:
            if not char.lower() in self.hotkey_manager.input_keys:
                self.show_message("无效快捷键", 5000)
                return
        if not key:
            self.show_message("无效快捷键", 5000)
            return

        shortcut_parts = []
        if self.ctrl_cb.GetValue():
            shortcut_parts.append("ctrl")
        if self.shift_cb.GetValue():
            shortcut_parts.append("shift")
        if self.alt_cb.GetValue():
            shortcut_parts.append("alt")

        if "ctrl" not in shortcut_parts:
            self.show_message("需勾选 Ctrl", 5000)
            return

        shortcut_parts.append(key.lower())
        shortcut = " ".join(shortcut_parts)

        self.config["shortcut"] = shortcut
        Config.save_config(self.config)
        self.hotkey_manager.hotkey = shortcut.split(' ')

        if self.is_active:
            self.hotkey_manager.stop_()
            self.hotkey_manager.start_()

        self.show_message("保存成功")

    def on_auto_start(self, event):
        self.config["auto_start"] = self.auto_start.GetValue()
        Config.save_config(self.config)

        if self.config['auto_start'] and not self.is_active:
            self.toggle_active(None)

    def on_key_char(self, event):
        if len(self.key_input.GetValue()) > 0:
            self.key_input.SetValue("")
        char = chr(event.GetKeyCode()).upper()
        self.key_input.SetValue(char)

    def toggle_active(self, event):
        app_id = self.config["app_id"]
        secret_key = self.config["secret_key"]

        if not app_id or not secret_key:
            self.show_message("请先填写 APP ID 和 密钥", 5000)
            return

        if not self.is_active:
            self.start_btn.SetLabel("开启中")
            self.is_active = True
            self.hotkey_manager.start_()
        else:
            self.start_btn.SetLabel("开 启")
            self.is_active = False
            self.hotkey_manager.stop_()

    def translate_text(self, text):
        app_id = self.config["app_id"]
        key = self.config["secret_key"]
        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        salt = random.randint(32768, 65536)

        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        sign = make_md5(app_id + text + str(salt) + key)

        to_lang = self.lang_codes.get(self.lang_choice.GetSelection(), "auto")

        params = {
            'q': text,
            'from': 'auto',
            'to': to_lang,
            'appid': app_id,
            'salt': salt,
            'sign': sign
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, params=params, headers=headers)

        if response.status_code == 200:
            result = response.json()
            if "trans_result" in result:
                return True, result['trans_result'][0]['dst']
            elif "error_msg" in result:
                return False, result["error_msg"]
            return False, None
        else:
            return False, None

    def perform_translation(self):
        wx.CallAfter(self.show_message, "翻译中 ...")

        try:
            pyperclip.copy('')
            sleep(0.1)
            keyboard.send('ctrl+c')
            sleep(0.1)

            # 获取复制的文本
            copied_text = pyperclip.paste()
            # print("复制的文本:", copied_text)
            if not copied_text.strip():
                wx.CallAfter(self.show_message, "没有选中文本", 5000)
                return

            success, translated_text = self.translate_text(copied_text)
            if success:
                pyperclip.copy(translated_text)
                sleep(0.1)
                keyboard.send('ctrl+v')
                wx.CallAfter(self.show_message, "翻译完成")
            else:
                if translated_text:
                    wx.CallAfter(self.show_message, f"失败，请检查设置: {translated_text}", 5000)
                else:
                    wx.CallAfter(self.show_message, "失败，请检查网络和设置", 5000)

        except Exception as e:
            # print("翻译出错:", str(e))
            wx.CallAfter(self.show_message, "出错，请检查网络", 5000)

    def show_message(self, message, duration=3000):
        self.version_text.Hide()

        # 显示消息
        self.message_text.SetLabel(message)
        self.message_text.Show()

        # 如果已有计时器在运行，先停止它
        if self.message_timer:
            self.message_timer.Stop()

        # 创建新的计时器
        self.message_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_message_timer, self.message_timer)
        self.message_timer.Start(duration, oneShot=True)  # 3秒后触发

        # 刷新布局
        self.panel.Layout()

    def _on_message_timer(self, event):
        self.message_text.Hide()
        self.version_text.Show()
        self.panel.Layout()
        self.message_timer.Stop()
        self.message_timer = None

    def about_click(self, event):
        dialog = wx.Dialog(self, title="关于", size=about_size)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # 基本信息
        info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        text_sizer = wx.BoxSizer(wx.VERTICAL)
        title_text = wx.StaticText(dialog, label=about_title_text)
        title_text.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        dev_text = wx.StaticText(dialog, label=f"开发者：{about_developer}")
        email_text = wx.StaticText(dialog, label=f"邮   箱：{about_email}")

        text_sizer.Add(title_text, 0)
        text_sizer.AddSpacer(8)
        text_sizer.Add(dev_text, 0)
        text_sizer.Add(email_text, 0)

        if os.path.exists(icon_image):
            img = wx.Image(icon_image, wx.BITMAP_TYPE_PNG)
            img = img.Scale(70, 70, wx.IMAGE_QUALITY_HIGH)
            icon_bitmap = wx.StaticBitmap(dialog, -1, wx.Bitmap(img))
            info_sizer.Add(text_sizer, 1, wx.EXPAND | wx.ALL, 10)
            info_sizer.Add(icon_bitmap, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        else:
            info_sizer.Add(text_sizer, 1, wx.EXPAND | wx.ALL, 10)

        left_sizer.AddSpacer(10)
        left_sizer.Add(info_sizer, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.AddSpacer(10)
        left_sizer.Add(CustomLine(dialog, colour=wx.Colour(custom_line_colour)), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        left_sizer.AddSpacer(20)

        # 致谢
        thanks_title = wx.StaticText(dialog, label="致谢")
        thanks_title.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        thanks_text = wx.StaticText(dialog, label=f"本程序使用了以下第三方库：\n{third_party_library}")
        thanks_text2 = wx.StaticText(dialog, label="在此向所有开源项目开发者表达感谢和敬意。")

        left_sizer.Add(thanks_title, 0, wx.LEFT | wx.RIGHT, 15)
        left_sizer.AddSpacer(8)
        left_sizer.Add(thanks_text, 0, wx.LEFT | wx.RIGHT, 15)
        left_sizer.AddSpacer(8)
        left_sizer.Add(thanks_text2, 0, wx.LEFT | wx.RIGHT, 15)
        left_sizer.AddSpacer(25)
        left_sizer.Add(CustomLine(dialog, colour=wx.Colour(custom_line_colour)), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        left_sizer.AddSpacer(20)

        # 赞助
        if os.path.exists(sponsor_image) and os.path.exists(dev_image):
            sponsor_title = wx.StaticText(dialog, label="赞助")
            sponsor_title.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            sponsor_text = wx.StaticText(dialog, label="微信扫码，赞助开发者")
            sponsor_text2 = wx.StaticText(dialog, label="你一块，我一块，bobo 就能吃鸡块 ヾ(^‿^)ノ")

            img = wx.Image(sponsor_image, wx.BITMAP_TYPE_PNG)
            img = img.Scale(280, 280, wx.IMAGE_QUALITY_HIGH)
            sponsor_panel_size = (300, 300)
            sponsor_panel = RotatingPanel(dialog, img, sponsor_panel_size, dev_image)
            sponsor_panel.SetMinSize(sponsor_panel_size)

            left_sizer.Add(sponsor_title, 0, wx.LEFT | wx.RIGHT, 15)
            left_sizer.AddSpacer(8)
            left_sizer.Add(sponsor_text, 0, wx.LEFT | wx.RIGHT, 15)
            left_sizer.AddSpacer(20)
            left_sizer.Add(sponsor_panel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            left_sizer.AddSpacer(10)
            left_sizer.Add(sponsor_text2, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # 右侧
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddSpacer(19)

        help_btn = wx.Button(dialog, label="帮 助", size=(100, 35))
        copy_email_btn = wx.Button(dialog, label="复制邮箱", size=(100, 35))
        project_btn = wx.Button(dialog, label="项目地址", size=(100, 35))
        changelog_btn = wx.Button(dialog, label="更新日志", size=(100, 35))
        close_btn = wx.Button(dialog, label="关 闭", size=(100, 35))

        for btn in [help_btn, copy_email_btn, project_btn, changelog_btn]:
            right_sizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            right_sizer.AddSpacer(10)

        right_sizer.AddStretchSpacer()
        right_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        right_sizer.AddSpacer(20)

        # 绑定事件
        def on_copy_email(evt):
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(about_email))
                wx.TheClipboard.Close()
                copy_email_btn.SetLabel("已复制")
                wx.CallLater(3000, lambda: copy_email_btn.SetLabel("复制邮箱"))

        help_btn.Bind(wx.EVT_BUTTON, lambda evt: webbrowser.open(help_url))
        copy_email_btn.Bind(wx.EVT_BUTTON, on_copy_email)
        project_btn.Bind(wx.EVT_BUTTON, lambda evt: webbrowser.open(project_url))
        changelog_btn.Bind(wx.EVT_BUTTON, lambda evt: webbrowser.open(changelog_url))
        close_btn.Bind(wx.EVT_BUTTON, lambda evt: dialog.Close())

        # 设置主布局
        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(CustomLine(dialog, colour=wx.Colour(custom_line_colour), is_vertical=True), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(right_sizer, 0, wx.EXPAND | wx.ALL, 10)

        dialog.SetSizer(main_sizer)
        dialog.Centre()
        dialog.ShowModal()
        dialog.Destroy()

    def on_close(self, event):
        self.hotkey_manager.stop_()
        event.Skip()


class RotatingPanel(wx.Panel):
    def __init__(self, parent, sponsor_image, sponsor_panel_size, dev_image):
        super().__init__(parent)
        self.sponsor_image = sponsor_image
        self.sponsor_panel_size = sponsor_panel_size
        self.dev_image = wx.Image(dev_image, wx.BITMAP_TYPE_PNG)
        self.dev_image = self.dev_image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)

        self.angle = 0
        self.timer = None

        # 计算旋转所需的最大空间
        img_width = self.sponsor_image.GetWidth()
        img_height = self.sponsor_image.GetHeight()
        self.max_size = math.ceil(math.sqrt(img_width ** 2 + img_height ** 2))

        # 创建内存缓冲位图
        self.buffer = wx.Bitmap(self.max_size, self.max_size)

        # 设置面板背景为透明
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # 绑定事件
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # 初始化缓冲
        self.init_buffer()

        # 启动定时器
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(50)  # 每50毫秒更新一次

    def init_buffer(self):
        """初始化缓冲"""
        dc = wx.MemoryDC()
        dc.SelectObject(self.buffer)
        self.draw(dc)
        dc.SelectObject(wx.NullBitmap)

    def draw(self, dc):
        """绘制图像到指定的DC"""
        # 使用透明背景
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        # 获取面板尺寸
        width, height = self.GetSize()

        # 创建图片副本并旋转
        img_copy = self.sponsor_image.Copy()
        img_center = wx.Point(self.sponsor_image.GetWidth() // 2,
                            self.sponsor_image.GetHeight() // 2)
        rotated_img = img_copy.Rotate(math.radians(self.angle),
                                    img_center, True)

        # 计算居中位置
        x = (width - rotated_img.GetWidth()) // 2
        y = (height - rotated_img.GetHeight()) // 2

        # 如果图片有alpha通道，确保使用它
        if rotated_img.HasAlpha():
            bitmap = wx.Bitmap(rotated_img)
        else:
            # 如果没有alpha通道，添加一个
            rotated_img.InitAlpha()
            bitmap = wx.Bitmap(rotated_img)

        dc.DrawBitmap(bitmap, x, y, True)  # True表示使用mask

        # 计算dev_image居中位置
        dev_x = (self.sponsor_panel_size[0] - self.dev_image.GetWidth()) // 2
        dev_y = (self.sponsor_panel_size[1] - self.dev_image.GetHeight()) // 2

        # 绘制图片
        dc.DrawBitmap(wx.Bitmap(self.dev_image), dev_x, dev_y, True)

    def on_paint(self, event):
        """处理绘制事件"""
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.buffer, 0, 0, True)

    def on_size(self, event):
        """处理尺寸改变事件"""
        self.init_buffer()
        event.Skip()

    def on_timer(self, event):
        """定时器事件处理"""
        self.angle = (self.angle - 0.2) % 360
        self.init_buffer()
        self.Refresh()

    def __del__(self):
        """清理定时器"""
        if self.timer:
            self.timer.Stop()


class CustomLine(wx.Panel):
    def __init__(self, parent, colour=wx.Colour(255, 0, 0), is_vertical=False):
        super().__init__(parent)
        self.colour = colour
        self.is_vertical = is_vertical
        self.SetBackgroundColour(wx.Colour("#ffffff"))
        self.Bind(wx.EVT_PAINT, self.on_paint)

        if is_vertical:
            self.SetMinSize((1, -1))
        else:
            self.SetMinSize((-1, 1))

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(self.colour, 1))

        w, h = self.GetSize()
        if self.is_vertical:
            dc.DrawLine(0, 0, 0, h)
        else:
            dc.DrawLine(0, 0, w, 0)


class TranslatorApp(wx.App):
    def OnInit(self):
        frame = TranslatorFrame()
        frame.Show()
        return True


if __name__ == '__main__':
    app = TranslatorApp()
    app.MainLoop()
