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
from animation_manager import PetAnimation  # 导入动画管理类
from textanimate import TextAnimation  # 导入文字动画类
from file_notes_manager import FileNotesManager  # 导入文件注释管理类
from translation_manager import TranslationManager  # 导入翻译管理类


class DeskAipet:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面宠物")
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-alpha', 0.9)  # 半透明效果
        
        # 初始化功能管理器
        self.file_notes_manager = FileNotesManager(self)
        self.translation_manager = TranslationManager(self)
        
        # 创建GUI
        self.create_gui()
        
        # 初始化动画管理器
        self.animation_manager = PetAnimation(self.pet_label)
        
        # 初始化文字动画
        sound_file = "typewriter.mp3"  
        if not os.path.exists(sound_file):
            sound_file = None
            
        self.text_animator = TextAnimation(self.dialog_text, sound_file=sound_file, delay=50)
        
        # 启动提醒线程
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        # 启动宠物待机动画
        self.start_idle_animation()
        
        # 显示欢迎消息（使用文字动画）
        self.root.after(100, self.show_welcome_message)
        
        # 当前显示的文本内容
        self.current_full_text = ""

    def show_welcome_message(self):
        """显示欢迎消息（使用文字动画）"""
        welcome_text = "你好！我是月见真。\n我可以帮你翻译英语、提醒保存文件，还能记住文件夹的注释。"
        self.current_full_text = welcome_text
        
        # 使用文字动画显示欢迎文本，并获取动画持续时间
        duration = self.text_animator.type_text(
            welcome_text, 
            callback=self.on_welcome_complete
        )
        
        # 同时播放说话动画，与文字动画同步
        self.animation_manager.play_talking_animation1(duration)

    def on_welcome_complete(self):
        """欢迎消息显示完成后的回调"""
        # 显示扩展按钮
        self.expand_button.pack(side='right', padx=5)

    def reminder_loop(self):
        """提醒循环"""
        reminder_interval = 1.5 * 60 * 60  # 1.5小时转换为秒
        
        while True:
            time.sleep(reminder_interval)
            # 提醒时显示说话动画和文字动画
            self.root.after(0, self.show_reminder)

    def show_reminder(self):
        """显示提醒（在主线程中执行）"""
        reminder_text = "提醒：请保存您的工作文件！"
        self.current_full_text = reminder_text
        
        # 使用文字动画显示提醒文本
        duration = self.text_animator.type_text(
            reminder_text,
            callback=self.on_reminder_complete
        )
        
        # 同时播放说话动画
        self.animation_manager.play_talking_animation2(duration)

    def on_reminder_complete(self):
        """提醒消息显示完成后的回调"""
        # 显示扩展按钮
        self.expand_button.pack(side='right', padx=5)

    def start_idle_animation(self):
        """开始待机动画循环"""
        def idle_loop():
            while True:
                # 播放待机动画10秒
                self.animation_manager.play_idle_animation(10)
                time.sleep(10)  
                
        # 启动待机动画循环线程
        idle_thread = threading.Thread(target=idle_loop, daemon=True)
        idle_thread.start()

    def create_gui(self):
        """创建GUI界面"""
        # 主框架
        self.main_frame = tk.Frame(self.root, bg='lightblue', bd=2, relief='solid')
        self.main_frame.pack(padx=5, pady=5)
        
        # 宠物头像 - 使用默认关闭表情
        default_image = Image.new('RGB', (80, 80), color='lightblue')
        self.default_photo = ImageTk.PhotoImage(default_image)
        self.pet_label = tk.Label(self.main_frame, image=self.default_photo, bg='lightblue')
        self.pet_label.pack(pady=5)
        
        # 对话框框架
        self.dialog_frame = tk.Frame(self.main_frame, bg='white', bd=1, relief='solid')
        self.dialog_frame.pack(fill='x', padx=5, pady=5)
        
        # 对话框文本 - 固定大小，高度3行，宽度25字符
        self.dialog_text = tk.Text(self.dialog_frame, height=3, width=25, wrap='word', 
                                  bg='white', fg='black', font=('Arial', 10))
        self.dialog_text.pack(padx=5, pady=5)
        # 初始文本将在初始化后通过文字动画显示
        self.dialog_text.config(state='disabled')
        
        # 扩展按钮框架（放在对话框下方）
        self.expand_frame = tk.Frame(self.main_frame, bg='lightblue')
        self.expand_frame.pack(fill='x', padx=5, pady=2)
        
        # 扩展按钮 - 初始隐藏，文字显示完成后显示
        self.expand_button = tk.Button(self.expand_frame, text="查看完整内容", 
                                      command=self.show_full_text, bg='lightgrey')
        self.expand_button.pack_forget()  # 初始隐藏
        
        # 功能按钮框架
        self.function_frame = tk.Frame(self.main_frame, bg='lightblue')
        self.function_frame.pack(fill='x', padx=5, pady=5)
        
        # 功能按钮
        self.function_btn = tk.Button(self.function_frame, text="功能菜单", 
                                     command=self.show_function_menu, bg='lightgreen')
        self.function_btn.pack(fill='x', padx=2)
        
        # 关闭按钮
        self.close_btn = tk.Button(self.function_frame, text="关闭", 
                                  command=self.root.quit, bg='pink')
        self.close_btn.pack(fill='x', padx=2, pady=2)
        
        # 绑定拖动事件
        self.pet_label.bind("<ButtonPress-1>", self.start_drag)
        self.pet_label.bind("<B1-Motion>", self.on_drag)
        self.pet_label.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 初始位置
        self.root.geometry("+100+100")

    def show_function_menu(self):
        """显示功能菜单"""
        # 创建功能菜单窗口
        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.title("功能菜单")
        self.menu_window.geometry("200x150")
        self.menu_window.attributes('-topmost', True)  # 菜单置顶
        self.menu_window.resizable(False, False)
        
        # 设置菜单位置（在主窗口旁边）
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()
        self.menu_window.geometry(f"+{x}+{y}")
        
        # 功能按钮
        read_notes_btn = tk.Button(self.menu_window, text="1. 读文件注释", 
                                  command=self.read_file_notes, width=20)
        read_notes_btn.pack(pady=5)
        
        add_notes_btn = tk.Button(self.menu_window, text="2. 添加文件注释", 
                                 command=self.add_file_notes, width=20)
        add_notes_btn.pack(pady=5)
        
        question_btn = tk.Button(self.menu_window, text="3. 提问", 
                                command=self.show_question, width=20)
        question_btn.pack(pady=5)
        
        translate_btn = tk.Button(self.menu_window, text="4. 翻译", 
                                 command=self.translate_text, width=20)
        translate_btn.pack(pady=5)
        
        # 绑定关闭事件
        self.menu_window.protocol("WM_DELETE_WINDOW", self.menu_window.destroy)

    def read_file_notes(self):
        """读取文件注释"""
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
        self.file_notes_manager.read_notes()

    def add_file_notes(self):
        """添加文件注释"""
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
        self.file_notes_manager.add_notes()

    def show_question(self):
        """显示提问功能（暂不支持）"""
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
        
        message = "暂时不支持提问功能"
        self.current_full_text = message
        
        # 隐藏扩展按钮
        self.expand_button.pack_forget()
        
        # 使用文字动画显示消息
        duration = self.text_animator.type_text(
            message,
            callback=lambda: self.expand_button.pack(side='right', padx=5)
        )
        
        # 播放否认动画
        self.animation_manager.play_denying_animation(duration)

    def translate_text(self):
        """翻译文本"""
        if hasattr(self, 'menu_window'):
            self.menu_window.destroy()
        self.translation_manager.translate()

    def show_full_text(self):
        """显示完整文本的弹窗"""
        # 创建弹窗
        self.full_text_window = tk.Toplevel(self.root)
        self.full_text_window.title("完整内容")
        self.full_text_window.geometry("400x300")
        self.full_text_window.attributes('-topmost', True)  # 弹窗置顶
        self.full_text_window.resizable(True, True)  # 允许调整大小
        
        # 设置弹窗位置（在主窗口旁边）
        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()
        self.full_text_window.geometry(f"+{x}+{y}")
        
        # 创建标题栏
        title_frame = tk.Frame(self.full_text_window, bg='lightgray', height=30)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)  # 防止内容改变框架大小
        
        # 标题
        title_label = tk.Label(title_frame, text="完整内容", bg='lightgray', fg='black')
        title_label.pack(side='left', padx=10, pady=5)
        
        # 关闭按钮（右上角X）
        close_btn = tk.Button(title_frame, text="✕", command=self.full_text_window.destroy,
                            bg='lightgray', fg='black', bd=0, font=('Arial', 12))
        close_btn.pack(side='right', padx=5, pady=5)
        
        # 文本框架
        text_frame = tk.Frame(self.full_text_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 完整文本显示区域
        full_text_widget = tk.Text(text_frame, wrap='word', yscrollcommand=scrollbar.set,
                                  bg='white', fg='black', font=('Arial', 10))
        full_text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=full_text_widget.yview)
        
        # 插入完整文本
        full_text_widget.insert('1.0', self.current_full_text)
        full_text_widget.config(state='disabled')  # 设置为只读
        
        # 绑定关闭事件
        self.full_text_window.protocol("WM_DELETE_WINDOW", self.full_text_window.destroy)

    def start_drag(self, event):
        """开始拖动"""
        self.is_dragging = True
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
    
    def on_drag(self, event):
        """拖动中"""
        if self.is_dragging:
            x = self.root.winfo_x() + (event.x_root - self.drag_start_x)
            y = self.root.winfo_y() + (event.y_root - self.drag_start_y)
            self.root.geometry(f"+{x}+{y}")
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
    
    def stop_drag(self, event):
        """停止拖动"""
        self.is_dragging = False

    def show_message(self, message, animation_type="talking1"):
        """显示消息（使用文字动画）"""
        self.current_full_text = message
        
        # 隐藏扩展按钮
        self.expand_button.pack_forget()
        
        # 启用文本控件以便插入文字
        self.dialog_text.config(state='normal')
        
        # 使用文字动画显示消息
        duration = self.text_animator.type_text(
            message,
            callback=lambda: self.dialog_text.config(state='disabled') or self.expand_button.pack(side='right', padx=5)
        )
        
        # 根据类型播放相应的动画
        if animation_type == "talking1":
            self.animation_manager.play_talking_animation1(duration)
        elif animation_type == "talking2":
            self.animation_manager.play_talking_animation2(duration)
        elif animation_type == "denying":
            self.animation_manager.play_denying_animation(duration)


def main():
    root = tk.Tk()
    pet = DeskAipet(root)
    root.mainloop()

if __name__ == "__main__":
    main()