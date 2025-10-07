import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import random
import hashlib
import json
import os

class TranslationManager:
    def __init__(self, pet_app):
        """
        翻译管理器
        
        Args:
            pet_app: 主程序实例，用于访问动画和显示功能
        """
        self.pet_app = pet_app
        self.config_file = "translation_config.json"
        
        # 加载配置
        self.appid, self.key = self._load_config()
        
        # 百度翻译API配置
        self.url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def _load_config(self):
        """从配置文件加载API配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('appid', ''), config.get('key', '')
            else:
                return '', ''
        except Exception as e:
            print(f"加载配置文件失败了: {e}")
            return '', ''

    def _save_config(self, appid, key):
        """保存API配置到文件"""
        try:
            config = {
                'appid': appid,
                'key': key
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败了: {e}")
            return False

    def _test_api(self, appid, key, text="test"):
        """测试API配置是否有效"""
        try:
            salt = str(random.randint(32768, 65536))
            sign = appid + text + salt + key
            sign = hashlib.md5(sign.encode()).hexdigest()
            
            params = {
                'q': text,
                'from': 'en',
                'to': 'zh',
                'appid': appid,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(self.url, params=params, timeout=5)
            result = response.json()
            
            # 检查是否有错误码
            if 'error_code' in result:
                return False, result.get('error_msg', '未知的错误呢……')
            else:
                return True, "API配置有效"
                
        except Exception as e:
            return False, f"API测试失败: {str(e)}"

    def translate(self):
        """翻译文本"""
        # 检查API配置
        if not self.appid or not self.key:
            self.pet_app.show_message("检测到你没有配置翻译的API呢，请先配置一下吧", "talking2")
            self.pet_app.root.after(1000, self._ask_for_api_config)
            return
        
        # 测试API配置是否有效
        is_valid, msg = self._test_api(self.appid, self.key)
        if not is_valid:
            self.pet_app.show_message("抱歉……感觉API不正确呢……能麻烦输入一下你的账户和密钥吗", "denying")
            self.pet_app.root.after(1000, self._ask_for_api_config)
            return
        
        # 显示提示消息
        self.pet_app.show_message("请输入要翻译的文字", "talking1")
        
        # 延迟一下，让消息显示完成后再弹出输入框
        self.pet_app.root.after(1000, self._ask_text_for_translation)

    def _ask_for_api_config(self):
        """请求用户输入API配置"""
        # 创建配置窗口
        config_window = tk.Toplevel(self.pet_app.root)
        config_window.title("配置百度翻译API")
        config_window.geometry("400x200")
        config_window.attributes('-topmost', True)
        config_window.resizable(False, False)
        
        # 设置窗口位置
        x = self.pet_app.root.winfo_x() + 50
        y = self.pet_app.root.winfo_y() + 50
        config_window.geometry(f"+{x}+{y}")
        
        # 播放说话动画
        self.pet_app.animation_manager.play_talking_animation2(10)  # 播放较长时间的动画
        
        # 应用ID输入框
        appid_frame = tk.Frame(config_window)
        appid_frame.pack(fill='x', padx=20, pady=10)
        
        appid_label = tk.Label(appid_frame, text="百度翻译APPID:")
        appid_label.pack(side='left')
        
        appid_entry = tk.Entry(appid_frame, width=30)
        appid_entry.pack(side='right', fill='x', expand=True)
        if self.appid:
            appid_entry.insert(0, self.appid)
        
        # 密钥输入框
        key_frame = tk.Frame(config_window)
        key_frame.pack(fill='x', padx=20, pady=10)
        
        key_label = tk.Label(key_frame, text="百度翻译密钥:")
        key_label.pack(side='left')
        
        key_entry = tk.Entry(key_frame, width=30, show="*")
        key_entry.pack(side='right', fill='x', expand=True)
        if self.key:
            key_entry.insert(0, self.key)
        
        # 按钮框架
        button_frame = tk.Frame(config_window)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def save_config():
            new_appid = appid_entry.get().strip()
            new_key = key_entry.get().strip()
            
            if not new_appid or not new_key:
                messagebox.showerror("发生错误了……", "APPID和密钥都不能为空", parent=config_window)
                return
            
            # 测试新配置是否有效
            is_valid, msg = self._test_api(new_appid, new_key)
            if is_valid:
                # 保存配置
                if self._save_config(new_appid, new_key):
                    self.appid = new_appid
                    self.key = new_key
                    config_window.destroy()
                    self.pet_app.show_message("API配置成功了！谢谢你！现在可以使用翻译功能了", "talking1")
                    # 延迟后开始翻译流程
                    self.pet_app.root.after(2000, self.translate)
                else:
                    messagebox.showerror("发生错误了……", "保存配置失败", parent=config_window)
            else:
                messagebox.showerror("API测试失败了耶……", f"API配置无效: {msg}", parent=config_window)
        
        def cancel_config():
            config_window.destroy()
            self.pet_app.show_message("已取消API配置", "denying")
        
        save_btn = tk.Button(button_frame, text="保存", command=save_config, bg='lightgreen')
        save_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="取消", command=cancel_config, bg='lightcoral')
        cancel_btn.pack(side='right', padx=10)
        
        # 绑定回车键
        config_window.bind('<Return>', lambda e: save_config())
        
        # 绑定关闭事件
        config_window.protocol("WM_DELETE_WINDOW", cancel_config)
        
        # 聚焦到第一个输入框
        appid_entry.focus_set()

    def _ask_text_for_translation(self):
        """询问要翻译的文本"""
        text = simpledialog.askstring("翻译", "请你输入要翻译的文字:", parent=self.pet_app.root)
        
        if text:
            self._perform_translation(text)
        else:
            self.pet_app.show_message("已取消翻译", "denying")

    def _perform_translation(self, text):
        """执行翻译"""
        try:
            # 检测语言
            from_lang = self._detect_language(text)
            to_lang = 'zh' if from_lang == 'en' else 'en'
            
            # 调用百度翻译API
            result = self._baidu_translate(text, from_lang, to_lang)
            
            if result:
                from_lang_name = "英文" if from_lang == 'en' else "中文"
                to_lang_name = "中文" if to_lang == 'zh' else "英文"
                
                message = f"{from_lang_name}:\n{text}\n\n{to_lang_name}:\n{result}"
                self.pet_app.show_message(message, "talking1")
            else:
                self.pet_app.show_message("翻译失败，请检查API配置", "denying")
                
        except Exception as e:
            self.pet_app.show_message(f"翻译时出错:\n{str(e)}", "denying")

    def _detect_language(self, text):
        """检测文本语言"""
        # 简单的语言检测：如果包含中文字符，则认为是中文，否则是英文
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return 'zh'
        return 'en'

    def _baidu_translate(self, text, from_lang, to_lang):
        """调用百度翻译API"""
        try:
            salt = str(random.randint(32768, 65536))
            sign = self.appid + text + salt + self.key
            sign = hashlib.md5(sign.encode()).hexdigest()
            
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': self.appid,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(self.url, params=params, timeout=10)
            result = response.json()
            
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                error_code = result.get('error_code', '未知错误')
                error_msg = result.get('error_msg', '未知错误')
                print(f"翻译API错误: {error_code} - {error_msg}")
                return None
                
        except Exception as e:
            print(f"调用翻译API时出错了: {e}")
            return None