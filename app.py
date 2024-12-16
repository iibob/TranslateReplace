import tkinter as tk
import json
import random
from hashlib import md5
import pyperclip
import requests
import keyboard


# 开启状态
enabled = False


def main():
    global enabled
    # 加载设置
    try:
        with open("config.json", "r") as f:
            saved_config = json.load(f)
            config = {
                'app_id': saved_config.get('app_id', ''),
                'key': saved_config.get('key', ''),
                'auto_start': saved_config.get('auto_start', False),
                'shortcut': saved_config.get('shortcut', 'ctrl+shift+f')
            }
    except FileNotFoundError:
        config = {
            'app_id': '',
            'key': '',
            'auto_start': False,
            'shortcut': 'ctrl+shift+f'
        }
        with open("config.json", "w") as f:
            json.dump(config, f)

    def parse_shortcut(shortcut):
        # 解析快捷键字符串并返回按键和字符
        keys = shortcut.lower().split('+')
        modifiers = []
        char = ''

        for key in keys:
            if key == 'ctrl':
                modifiers.append('ctrl')
            elif key == 'shift':
                modifiers.append('shift')
            elif key == 'alt':
                modifiers.append('alt')
            else:
                char = key

        return modifiers, char

    def save_app_id_and_key():
        config['app_id'] = app_id_entry.get()
        config['key'] = key_entry.get()

        if config['app_id'] and config['key']:
            with open("config.json", "r") as f:
                saved_config = json.load(f)

            saved_config['app_id'] = config['app_id']
            saved_config['key'] = config['key']

            with open("config.json", "w") as f:
                json.dump(saved_config, f)

            show_message("已保存")
        else:
            show_message("ID 或 密钥 不能为空")

    def save_shortcut():
        chosen_keys = []
        if ctrl_var.get():
            chosen_keys.append("ctrl")
        if shift_var.get():
            chosen_keys.append("shift")
        if alt_var.get():
            chosen_keys.append("alt")

        char = char_entry.get().strip()

        # 检查是否至少勾选了一个修饰键
        if not chosen_keys:
            show_message("至少选择一个修饰键（Ctrl 或 Alt）")
            return

        # 检查字符是否有效（不为空且只有一个字符）
        if not char:
            show_message("请在输入框填写一个字母")
            return
        elif len(char) != 1:
            show_message("只能输入一个字母")
            return

        # 检查按键组合是否有效（不能仅由shift和char组成）
        if len(chosen_keys) == 1 and chosen_keys[0] == 'shift':
            show_message("至少选择一个修饰键（Ctrl 或 Alt）")
            return

        chosen_keys.append(char)
        shortcut_key = '+'.join(chosen_keys)

        with open("config.json", "r") as f:
            saved_config = json.load(f)

        saved_config['shortcut'] = shortcut_key

        with open("config.json", "w") as f:
            json.dump(saved_config, f)

        config['shortcut'] = shortcut_key

        # 如果已启用，重新注册快捷键
        if enabled:
            keyboard.unhook_all_hotkeys()
            keyboard.add_hotkey(config['shortcut'], perform_translation)

        show_message("已保存")

    def toggle_translate():
        global enabled
        if not config['app_id'] or not config['key']:
            show_message("请在设置中填写 ID 和 密钥")
            return

        if enabled:
            enabled = False
            open_button.config(text="开启")
            keyboard.unhook_all_hotkeys()
        else:
            enabled = True
            open_button.config(text="开启中")
            keyboard.add_hotkey(config['shortcut'], perform_translation)

    def perform_translation():
        old_text = pyperclip.paste()
        keyboard.press_and_release("ctrl+c")
        window.after(100)  # 等待剪贴板更新

        text = pyperclip.paste()
        if old_text == text or not text.strip():
            show_message("剪贴板中没有文本内容")
            return

        translated_text = translate_text(text, config['app_id'], config['key'])
        if translated_text:
            # pyperclip.copy(translated_text)  # 将翻译结果复制到剪贴板
            keyboard.write(translated_text)  # 将翻译结果写入到当前输入框
        else:
            show_message("翻译失败，请检查网络和设置")

    def toggle_auto_start():
        config['auto_start'] = auto_start_var.get()

        with open("config.json", "r") as f:
            saved_config = json.load(f)

        saved_config['auto_start'] = config['auto_start']

        with open("config.json", "w") as f:
            json.dump(saved_config, f)

        if config['auto_start'] and not enabled:
            toggle_translate()

    def translate_text(text, app_id, key):
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
            return result['trans_result'][0]['dst']
        else:
            return None

    def show_message(msg):
        message_label.config(text=msg, fg='red')
        message_label.pack(side="bottom", fill="x", padx=10, pady=(0, 4))
        window.after(3000, lambda: message_label.config(text=message_label_text, fg=message_label_colour))

    def toggle_settings_view():
        # 切换设置部分的显示与隐藏
        if settings_frame.winfo_ismapped():  # 判断settings_frame是否已经显示
            settings_frame.pack_forget()
            window.geometry(size_1)  # 恢复窗口尺寸
            settings_button.config(text="设置")
        else:
            settings_frame.pack(pady=10)
            window.geometry(size_2)  # 增大窗口尺寸
            settings_button.config(text="隐藏设置")

    # 主窗口
    size_1 = '350x190'
    size_2 = '350x540'
    window = tk.Tk()
    window.title("翻译助手")

    # 禁止调整窗口大小
    window.resizable(False, False)

    # 获取屏幕的宽度和高度
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # 获取窗口的宽度和高度
    parts = size_1.split('x')
    window_width = int(parts[0])
    window_height = int(parts[1])

    # 计算窗口的位置
    position_top = int((screen_height * 0.8 - window_height) / 2)
    position_left = int((screen_width - window_width) / 2)

    # 设置窗口位置
    window.geometry(f'{size_1}+{position_left}+{position_top}')

    window.iconbitmap('icon.ico')

    # 启用按钮
    open_button = tk.Button(window, text="开启", command=toggle_translate, width=18, height=2, font=("", 12, "bold"))
    open_button.pack(pady=(28, 2))

    # 自动开启选项
    auto_start_var = tk.BooleanVar(value=config['auto_start'])
    auto_start_checkbox = tk.Checkbutton(window, text="自动开启", variable=auto_start_var, command=toggle_auto_start)
    auto_start_checkbox.pack(pady=(2, 5))

    # 设置和退出按钮容器
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    settings_button = tk.Button(button_frame, text="设置", command=toggle_settings_view, width=10)
    settings_button.pack(side="left", padx=5)

    quit_button = tk.Button(button_frame, text="退出", command=lambda: window.destroy(), width=10)
    quit_button.pack(side="left", padx=5)

    # 消息标签
    message_label_text = '© 2024   @iiboob   V0.1'
    message_label_colour = '#9d9d9d'
    message_label = tk.Label(window, text=message_label_text, fg=message_label_colour)
    message_label.pack(side="bottom", fill="x", padx=10, pady=(0, 4))

    # 设置
    settings_frame = tk.Frame(window)

    # 第一部分：ID 和 KEY
    id_key_frame = tk.LabelFrame(settings_frame, text="百度翻译", padx=10, pady=10)
    id_key_frame.pack(fill="x")

    # APP ID 标签和输入框
    tk.Label(id_key_frame, text="APP ID:").pack(anchor="w", pady=0)
    app_id_entry = tk.Entry(id_key_frame, width=40)
    app_id_entry.insert(0, config['app_id'])
    app_id_entry.pack()

    # KEY 标签和输入框
    tk.Label(id_key_frame, text="密钥:").pack(anchor="w", pady=(10, 0))
    key_entry = tk.Entry(id_key_frame, width=40)
    key_entry.insert(0, config['key'])
    key_entry.pack()

    # 保存按钮
    save_app_key_button = tk.Button(id_key_frame, text="保 存", command=save_app_id_and_key, width=39)
    save_app_key_button.pack(pady=(16, 10))

    # 第二部分：快捷键设置
    shortcut_frame = tk.LabelFrame(settings_frame, text="快捷键", padx=10, pady=10)
    shortcut_frame.pack(fill="x", pady=(20, 0))

    # 创建容器
    modifiers_frame = tk.Frame(shortcut_frame)
    modifiers_frame.grid(row=0, column=0)

    # 按钮选择：Ctrl、Shift、Alt
    ctrl_var = tk.BooleanVar()
    shift_var = tk.BooleanVar()
    alt_var = tk.BooleanVar()
    ctrl_button = tk.Checkbutton(modifiers_frame, text="Ctrl", variable=ctrl_var)
    ctrl_button.grid(row=0, column=0, padx=(0, 8))
    shift_button = tk.Checkbutton(modifiers_frame, text="Shift", variable=shift_var)
    shift_button.grid(row=0, column=1, padx=8)
    alt_button = tk.Checkbutton(modifiers_frame, text="Alt", variable=alt_var)
    alt_button.grid(row=0, column=2, padx=8)

    # 输入框
    char_entry = tk.Entry(modifiers_frame, width=5)
    char_entry.grid(row=0, column=3, padx=(10, 0))

    # 根据配置设置修饰键复选框和输入框
    if config['shortcut']:
        modifiers, char = parse_shortcut(config['shortcut'])

        ctrl_var.set('ctrl' in modifiers)
        shift_var.set('shift' in modifiers)
        alt_var.set('alt' in modifiers)

        char_entry.insert(0, char)

    # 保存快捷键按钮
    save_shortcut_button = tk.Button(shortcut_frame, text="保 存", command=save_shortcut, width=39)
    save_shortcut_button.grid(row=1, column=0, pady=10)

    # 自动开启
    if config['auto_start'] and config['app_id'] and config['key']:
        enabled = True
        open_button.config(text="开启中")
        keyboard.add_hotkey(config['shortcut'], perform_translation)

    # 运行主窗口
    window.mainloop()



# 空白复制会使用历史进行翻译的问题

if __name__ == "__main__":
    main()