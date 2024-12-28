import wx
import os
import json
import keyboard
import pyperclip
import random
from hashlib import md5
import requests
import webbrowser


panel_size = (400, 200)
panel_add_settings_size = (400, 575)
about_size = (550, 755)
CONFIG_FILE = "config.json"
custom_line_colour = "#d2d2d2"
about = "v0.2.0  ·  帮助  ·  反馈  ·  赞助"
about_title_text = "翻译助手 v0.2.0"
about_developer = "iibob"
about_email = 'iibobapp@gmail.com'
third_party_library = "wxPython、keyboard、pyperclip、requests"
help_url = "https://www.yuque.com/bo_o/box/pma7zu#PVjrc"
project_url = "https://github.com/iibob/TranslateReplace"
changelog_url = "https://www.yuque.com/bo_o/box/pma7zu#AGCCR"


class Config:
    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            default_config = {
                "app_id": "",
                "secret_key": "",
                "shortcut": "ctrl+shift+F",
                "auto_start": False
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)


class TranslatorFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="翻译助手", size=panel_size, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        # 设置窗口图标
        if os.path.exists("icon.png"):
            icon = wx.Icon("icon.png", wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon)

        # 加载配置
        self.config = Config.load_config()
        self.is_active = False

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
        main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
        main_sizer.AddSpacer(5)

        # 第二栏：自动开启选项
        auto_start_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.auto_start = wx.CheckBox(self.panel, label="自动开启")
        auto_start_sizer.Add(self.auto_start, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 5)
        main_sizer.Add(auto_start_sizer, 0, wx.ALIGN_CENTER)
        main_sizer.AddSpacer(20)
        self.auto_start.SetValue(self.config["auto_start"])

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
        key = saved_shortcut.split("+")[-1] if "+" in saved_shortcut else saved_shortcut
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

        # 自定义分隔线
        self.custom_line = CustomLine(self.panel, colour=wx.Colour(custom_line_colour))
        main_sizer.Add(self.custom_line, 0, wx.EXPAND)

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

        main_sizer.Add(version_sizer, 0, wx.ALIGN_CENTER | wx.TOP, 8)

        self.panel.SetSizer(main_sizer)
        self.Centre()
        
        # 绑定事件
        self.start_btn.Bind(wx.EVT_BUTTON, self.toggle_active)
        self.settings_btn.Bind(wx.EVT_BUTTON, self.toggle_settings)
        baidu_save_btn.Bind(wx.EVT_BUTTON, self.save_baidu_settings)
        shortcut_save_btn.Bind(wx.EVT_BUTTON, self.save_shortcut)
        help_btn.Bind(wx.EVT_BUTTON, lambda evt: webbrowser.open(help_url))
        self.version_text.Bind(wx.EVT_LEFT_DOWN, self.about_click)
        self.auto_start.Bind(wx.EVT_CHECKBOX, self.on_auto_start)
        self.key_input.Bind(wx.EVT_CHAR, self.on_key_char)

        # 初始化消息显示相关的属性
        self.message_timer = None
        
        # 根据配置文件自动激活程序
        if self.config["auto_start"]:
            self.toggle_active(None)

    def toggle_settings(self, event):
        if self.settings_panel.IsShown():
            self.settings_panel.Hide()
            self.custom_line.Show()
            self.settings_btn.SetLabel("设置")
            self.SetSize(panel_size)
        else:
            self.settings_panel.Show()
            self.custom_line.Hide()
            self.settings_btn.SetLabel("隐藏")
            self.SetSize(panel_add_settings_size)
        self.panel.Layout()

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
            if ord(char) < 32:
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
        shortcut = "+".join(shortcut_parts)

        try:
            keyboard.remove_hotkey(self.config["shortcut"])
        except:
            pass

        self.config["shortcut"] = shortcut
        Config.save_config(self.config)

        if self.is_active:
            keyboard.add_hotkey(shortcut, self.perform_translation)

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
            keyboard.add_hotkey(self.config["shortcut"], self.perform_translation)
        else:
            self.start_btn.SetLabel("开 启")
            self.is_active = False
            keyboard.remove_hotkey(self.config["shortcut"])

    def translate_text(self, text):
        app_id = self.config["app_id"]
        key = self.config["secret_key"]
        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        salt = random.randint(32768, 65536)

        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        sign = make_md5(app_id + text + str(salt) + key)

        params = {
            'q': text,
            'from': 'auto',
            'to': 'auto',
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
        if self.is_active:
            try:
                pyperclip.copy('')

                # 等待快捷键释放
                shortcut_parts = self.config["shortcut"].lower().split("+")
                while any(keyboard.is_pressed(key) for key in shortcut_parts):
                    wx.MilliSleep(50)
                wx.MilliSleep(100)

                keyboard.send('ctrl+c')
                wx.MilliSleep(100)
                
                # 获取复制的文本
                copied_text = pyperclip.paste()
                # print("复制的文本:", copied_text)
                if not copied_text.strip():
                    wx.CallAfter(self.show_message, "没有选中文本", 5000)
                    return

                success, translated_text = self.translate_text(copied_text)
                if success:
                    pyperclip.copy(translated_text)
                    wx.MilliSleep(100)
                    keyboard.send('ctrl+v')
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
        
        if os.path.exists("icon.png"):
            img = wx.Image("icon.png", wx.BITMAP_TYPE_PNG)
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
        if os.path.exists("sponsor.png"):
            sponsor_title = wx.StaticText(dialog, label="赞助")
            sponsor_title.SetFont(wx.Font(17, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            sponsor_text = wx.StaticText(dialog, label="微信扫码，赞助开发者")
            sponsor_text2 = wx.StaticText(dialog, label="你一块，我一块，bobo 就能吃鸡块 ヾ(^‿^)ノ")

            img = wx.Image("sponsor.png", wx.BITMAP_TYPE_PNG)
            img = img.Scale(280, 280, wx.IMAGE_QUALITY_HIGH)
            sponsor_bitmap = wx.StaticBitmap(dialog, -1, wx.Bitmap(img))

            left_sizer.Add(sponsor_title, 0, wx.LEFT | wx.RIGHT, 15)
            left_sizer.AddSpacer(8)
            left_sizer.Add(sponsor_text, 0, wx.LEFT | wx.RIGHT, 15)
            left_sizer.AddSpacer(20)
            left_sizer.Add(sponsor_bitmap, 0, wx.ALL | wx.ALIGN_CENTER, 5)
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
    
    def copy_to_clipboard(self, text):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            self.show_message("已复制到剪贴板", 3000)


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
