# coding=utf-8
# @Time     : 2025/01/17 18:36
# @File     : hotkey_manager.py
# @Software : PyCharm

from pynput import keyboard
from time import time


class HotkeyManager:
    """简易判断，仅判断左右Ctrl、Shift、Alt键，以及由 字母 数字 标点符号 组成组合键的这部分按键的释放情况。"""
    def __init__(self, hotkey_callback):
        self.hotkey_callback = hotkey_callback
        self.pressed_keys = set()
        self.keyboard_listener = None
        self.combination_matched = False
        self.last_press_time = time()
        self.hotkey = []
        self.modifier_keys = ['ctrl_l', 'ctrl_r', 'shift', 'shift_r', 'alt_l', 'alt_gr', 'cmd', 'cmd_r']
        # 自定义快捷键 字母、数字、标点符号 限制列表
        self.input_keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '`', '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/']
        self.key_mapping = {
            '48': '0',
            '49': '1',
            '50': '2',
            '51': '3',
            '52': '4',
            '53': '5',
            '54': '6',
            '55': '7',
            '56': '8',
            '57': '9',
            '65': 'a',
            '66': 'b',
            '67': 'c',
            '68': 'd',
            '69': 'e',
            '70': 'f',
            '71': 'g',
            '72': 'h',
            '73': 'i',
            '74': 'j',
            '75': 'k',
            '76': 'l',
            '77': 'm',
            '78': 'n',
            '79': 'o',
            '80': 'p',
            '81': 'q',
            '82': 'r',
            '83': 's',
            '84': 't',
            '85': 'u',
            '86': 'v',
            '87': 'w',
            '88': 'x',
            '89': 'y',
            '90': 'z',
            '96': 'Numpad_0',
            '97': 'Numpad_1',
            '98': 'Numpad_2',
            '99': 'Numpad_3',
            '100': 'Numpad_4',
            '101': 'Numpad_5',
            '12': 'Numpad_5',
            '102': 'Numpad_6',
            '103': 'Numpad_7',
            '104': 'Numpad_8',
            '105': 'Numpad_9',
            '106': 'Numpad_*',
            '107': 'Numpad_+',
            '109': 'Numpad_-',
            '110': 'Numpad_.',
            '111': 'Numpad_/',
            '186': ';',
            '187': '=',
            '188': ',',
            '189': '-',
            '190': '.',
            '191': '/',
            '192': '`',
            '219': '[',
            '220': '\\',
            '221': ']',
            '222': "'"
        }

    def on_press(self, key):
        """键盘按键按下时的回调"""
        # 清空按键集合。
        # 某些情况下（如使用 ahk 改键后），释放按键时不会成功从按键集合中移除，导致后续正确按下快捷键时，无法触发回调
        current_time = time()
        time_diff = current_time - self.last_press_time
        self.last_press_time = current_time
        if time_diff >= 5:
            self.pressed_keys.clear()

        new_kry = self.update_pressed_keys(key)
        if new_kry not in self.pressed_keys:
            # print(f'按下 {new_kry}')
            self.pressed_keys.add(new_kry)

            if self.check_elements():
                self.combination_matched = True
            else:
                self.combination_matched = False

    def on_release(self, key):
        """键盘释放按下时的回调"""
        new_kry = self.update_pressed_keys(key)
        self.pressed_keys.discard(new_kry)
        self.last_press_time = time()
        # print(f'松开 {new_kry} ----------------------------------------')

        # 判断已触发热键，并且所有按键都已释放
        if self.combination_matched and not self.pressed_keys:
            self.hotkey_callback()
            self.combination_matched = False

    def update_pressed_keys(self, key):
        """根据映射更新按键名称"""
        try:
            try:
                new_kry = str(key.vk)
            except:
                new_kry = str(key.name)
        except:
            # 经过这里获取的键值可能不能在释放按键时正确移除
            # 比如 Ctrl t，按下时 t 为 \x14，先释放 Ctrl 再释放 t 时，t 为 t，导致 \x14 无法移除
            new_kry = str(key).strip("'").replace("Key.", "").lower()
            # print("按键按下/释放时，传递过来的参数 key 不在预期")

        target_key = self.key_mapping.get(new_kry, new_kry)
        return target_key

    def check_elements(self):
        """判断按下的按键是否是热键"""
        if len(self.pressed_keys) != len(self.hotkey):
            return False

        equivalent_keys = {
            'ctrl': ['ctrl_l', 'ctrl_r'],
            'shift': ['shift', 'shift_r'],
            'alt': ['alt_l', 'alt_gr'],
            'cmd': ['cmd', 'cmd_r']
        }

        def check_key(key):
            if key in equivalent_keys:
                for equivalent_key in equivalent_keys[key]:
                    if equivalent_key in self.pressed_keys:
                        return True
                return False
            else:
                return key in self.pressed_keys

        result = []
        for item in self.hotkey:
            result.append(check_key(item))
        if all(result):
            return True
        else:
            return False

    def start_(self):
        """启动热键监听"""
        self.pressed_keys.clear()
        if not self.keyboard_listener:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.keyboard_listener.start()
            return True
        return False

    def stop_(self):
        """停止热键监听"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener.join()
            self.keyboard_listener = None
            return True
        return False

    def is_running(self):
        """检查热键监听器是否运行中"""
        return self.keyboard_listener is not None
