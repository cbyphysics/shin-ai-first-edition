import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
import json
import os
from PIL import Image, ImageTk
import requests
import hashlib
import uuid
import random

class Translater:
    def __init__(
        self  
    ):
        self.root = tk.Tk() 



    def translate_text(self):
        text = simpledialog.askstring("这里是月见真翻译员", "请你输入要翻译的英文文本:")
        if text:
            # 开始说话动画
            self.start_talking_animation()
            try:
                translation = self.baidu_translate(text, 'en', 'zh')
                self.show_message(f"翻译结果是: {translation}")
            except Exception as e:
                # 翻译失败时显示否认动画
                self.start_denying_animation()
                self.show_message(f"翻译失败: {str(e)}")
    
    def baidu_translate(self, text, from_lang='auto', to_lang='zh'):
        """
        使用百度翻译API进行翻译
        """
        # 如果未配置API密钥，使用模拟翻译
        if self.baidu_appid == '您的百度翻译APPID' or self.baidu_key == '您的百度翻译密钥':
            return self.fallback_translate(text)
        
        salt = str(random.randint(32768, 65536))
        sign = self.baidu_appid + text + salt + self.baidu_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        
        url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.baidu_appid,
            'salt': salt,
            'sign': sign
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                raise Exception(f"百度翻译API错误: {error_msg}")
            
            if 'trans_result' in result:
                translated_text = '\n'.join([item['dst'] for item in result['trans_result']])
                return translated_text
            else:
                raise Exception("找不到翻译结果")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"翻译处理失败: {str(e)}")
    
