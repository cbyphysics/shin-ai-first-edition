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

class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面宠物")
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-alpha', 0.9)  # 半透明效果
        
        # 百度翻译API配置 - 请替换为您自己的API密钥
        self.baidu_appid = '您的百度翻译APPID'  # 请在百度翻译开放平台申请
        self.baidu_key = '您的百度翻译密钥'     # 请在百度翻译开放平台申请
        
        # 宠物状态
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # 文件夹注释存储文件
        self.notes_file = "folder_notes.txt"
        self.folder_notes = self.load_folder_notes()
        
        # 创建GUI
        self.create_gui()
        
        # 启动提醒线程
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        # 启动宠物动画
        self.animate_pet()
    
    def create_gui(self):
        # 主框架
        self.main_frame = tk.Frame(self.root, bg='lightblue', bd=2, relief='solid')
        self.main_frame.pack(padx=5, pady=5)
        
        # 宠物头像
        self.pet_image = self.create_pet_image()
        self.pet_label = tk.Label(self.main_frame, image=self.pet_image, bg='lightblue')
        self.pet_label.pack(pady=5)
        
        # 对话框
        self.dialog_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid')
        self.dialog_frame.pack(fill='x', padx=5, pady=5)
        
        self.dialog_text = tk.Text(self.dialog_frame, height=3, width=25, wrap='word', 
                                  bg='white', fg='black', font=('Arial', 10))
        self.dialog_text.pack(padx=5, pady=5)
        self.dialog_text.insert('1.0', "你好！我是你的桌面宠物。\n我可以帮你翻译英语、提醒保存文件，还能记住文件夹的注释。")
        self.dialog_text.config(state='disabled')
        
        # 按钮框架
        self.button_frame = tk.Frame(self.main_frame, bg='lightblue')
        self.button_frame.pack(fill='x', padx=5, pady=5)
        
        # 翻译按钮
        self.translate_btn = tk.Button(self.button_frame, text="翻译英语", 
                                      command=self.translate_text, bg='lightgreen')
        self.translate_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # 添加文件夹注释按钮
        self.add_note_btn = tk.Button(self.button_frame, text="添加文件夹注释", 
                                     command=self.add_folder_note, bg='lightyellow')
        self.add_note_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # 查询文件夹注释按钮
        self.query_note_btn = tk.Button(self.button_frame, text="查询文件夹注释", 
                                       command=self.query_folder_note, bg='lightcoral')
        self.query_note_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # 关闭按钮
        self.close_btn = tk.Button(self.button_frame, text="关闭", 
                                  command=self.root.quit, bg='pink')
        self.close_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # 绑定拖动事件
        self.pet_label.bind("<ButtonPress-1>", self.start_drag)
        self.pet_label.bind("<B1-Motion>", self.on_drag)
        self.pet_label.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 初始位置
        self.root.geometry("+100+100")
    
    def create_pet_image(self):
        # 创建一个简单的宠物图像（实际应用中可以使用真实图片）
        image = Image.new('RGB', (80, 80), color='lightblue')
        # 添加简单的面部特征
        return ImageTk.PhotoImage(image)
    
    def start_drag(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def on_drag(self, event):
        if self.is_dragging:
            x = self.root.winfo_x() + (event.x_root - self.drag_start_x)
            y = self.root.winfo_y() + (event.y_root - self.drag_start_y)
            self.root.geometry(f"+{x}+{y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def stop_drag(self, event):
        self.is_dragging = False
    
    def animate_pet(self):
        # 简单的动画效果 - 改变宠物大小
        def animate():
            size = 80
            while True:
                for i in range(5):
                    new_size = size + i
                    image = Image.new('RGB', (new_size, new_size), color='lightblue')
                    self.pet_image = ImageTk.PhotoImage(image)
                    self.pet_label.config(image=self.pet_image)
                    time.sleep(0.1)
                for i in range(5, 0, -1):
                    new_size = size + i
                    image = Image.new('RGB', (new_size, new_size), color='lightblue')
                    self.pet_image = ImageTk.PhotoImage(image)
                    self.pet_label.config(image=self.pet_image)
                    time.sleep(0.1)
        
        threading.Thread(target=animate, daemon=True).start()
    
    def translate_text(self):
        text = simpledialog.askstring("翻译", "请输入要翻译的英文文本:")
        if text:
            try:
                translation = self.baidu_translate(text, 'en', 'zh')
                self.show_message(f"翻译结果: {translation}")
            except Exception as e:
                self.show_message(f"翻译失败: {str(e)}")
    
    def baidu_translate(self, text, from_lang='auto', to_lang='zh'):
        """
        使用百度翻译API进行翻译
        :param text: 要翻译的文本
        :param from_lang: 源语言，默认auto（自动检测）
        :param to_lang: 目标语言，默认zh（中文）
        :return: 翻译结果
        """
        # 如果未配置API密钥，使用模拟翻译
        if self.baidu_appid == '您的百度翻译APPID' or self.baidu_key == '您的百度翻译密钥':
            return self.fallback_translate(text)
        
        # 生成随机数
        salt = str(random.randint(32768, 65536))
        # 计算签名
        sign = self.baidu_appid + text + salt + self.baidu_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        
        # 构造请求URL
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
            # 发送请求
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            # 检查是否有错误
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                raise Exception(f"百度翻译API错误: {error_msg}")
            
            # 提取翻译结果
            if 'trans_result' in result:
                translated_text = '\n'.join([item['dst'] for item in result['trans_result']])
                return translated_text
            else:
                raise Exception("未找到翻译结果")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"翻译处理失败: {str(e)}")
    
    def fallback_translate(self, text):
        """
        备用翻译方法（当百度翻译API未配置时使用）
        """
        translations = {
            "hello": "你好",
            "world": "世界",
            "good morning": "早上好",
            "thank you": "谢谢",
            "goodbye": "再见",
            "file": "文件",
            "save": "保存",
            "folder": "文件夹",
            "note": "注释",
            "computer": "电脑",
            "program": "程序",
            "python": "Python编程语言",
            "desktop": "桌面",
            "pet": "宠物"
        }
        
        text_lower = text.lower().strip()
        if text_lower in translations:
            return translations[text_lower]
        else:
            # 如果找不到精确匹配，返回模拟翻译结果
            return f"'{text}' 的翻译结果（请配置百度翻译API获得准确翻译）"
    
    def reminder_loop(self):
        # 每1.5小时提醒保存文件
        reminder_interval = 1.5 * 60 * 60  # 1.5小时转换为秒
        
        while True:
            time.sleep(reminder_interval)
            self.show_message("提醒：请保存您的工作文件！")
    
    def show_message(self, message):
        # 在主线程中显示消息
        self.root.after(0, lambda: messagebox.showinfo("桌面宠物", message))
    
    def load_folder_notes(self):
        # 从文件加载文件夹注释
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_folder_notes(self):
        # 保存文件夹注释到文件
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.folder_notes, f, ensure_ascii=False, indent=2)
    
    def add_folder_note(self):
        folder_path = simpledialog.askstring("添加文件夹注释", "请输入文件夹路径:")
        if folder_path:
            if os.path.isdir(folder_path):
                note = simpledialog.askstring("添加文件夹注释", f"请输入对文件夹 '{folder_path}' 的注释:")
                if note:
                    self.folder_notes[folder_path] = note
                    self.save_folder_notes()
                    self.show_message(f"已为文件夹 '{folder_path}' 添加注释: {note}")
            else:
                self.show_message("指定的路径不是文件夹或不存在！")
    
    def query_folder_note(self):
        folder_path = simpledialog.askstring("查询文件夹注释", "请输入要查询的文件夹路径:")
        if folder_path:
            if folder_path in self.folder_notes:
                note = self.folder_notes[folder_path]
                self.show_message(f"文件夹 '{folder_path}' 的注释: {note}")
            else:
                self.show_message(f"未找到文件夹 '{folder_path}' 的注释。")

def main():
    root = tk.Tk()
    pet = DesktopPet(root)
    root.mainloop()

if __name__ == "__main__":
    main()