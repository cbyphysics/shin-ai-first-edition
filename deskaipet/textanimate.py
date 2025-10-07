import tkinter as tk
import pygame
import os

class TextAnimation:
    def __init__(self, text_widget, sound_file=None, delay=50):
        """
        初始化文字动画效果
        
        参数:
            text_widget: tkinter文本控件
            sound_file: 音效文件路径 (MP3格式)
            delay: 每个字之间的延迟时间(毫秒)
        """
        self.text_widget = text_widget
        self.sound_file = sound_file
        self.delay = delay / 1000.0  # 转换为秒
        self.is_playing = False
        self.current_task = None
        self.total_duration = 0  # 存储总时长
        
        # 初始化pygame音效系统
        self.sound = None
        if sound_file and os.path.exists(sound_file):
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.sound = pygame.mixer.Sound(sound_file)
                print(f"音效文件加载成功: {sound_file}")
            except Exception as e:
                self.sound = None
                print(f"无法加载音效文件: {sound_file}, 错误: {e}")
        else:
            if sound_file:
                print(f"音效文件不存在: {sound_file}")
            else:
                print("未提供音效文件，将使用无音效模式")
    
    def calculate_duration(self, text):
        """
        计算显示给定文本所需的总时间
        
        参数:
            text: 要显示的文本
            
        返回:
            总时间(秒)
        """
        # 总时间 = (字符数 - 1) * 每个字符的延迟时间
        # 减1是因为第一个字符没有延迟
        char_count = len(text)
        if char_count <= 1:
            return 0
        return (char_count - 1) * self.delay
    
    def type_text(self, text, tag=None, callback=None):
        """
        开始逐字显示文本
        
        参数:
            text: 要显示的文本
            tag: 文本标签(用于样式)
            callback: 动画完成后的回调函数
            
        返回:
            动画总时长(秒)
        """
        # 如果已经有动画在运行，先停止它
        if self.is_playing:
            self.stop()
        
        # 清空文本控件并重置状态
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.is_playing = True
        self.current_text = text
        self.current_index = 0
        self.current_tag = tag
        self.callback = callback
        
        # 计算总时长
        self.total_duration = self.calculate_duration(text)
        
        # 开始动画
        self._type_next_char()
        
        # 返回总时长
        return self.total_duration
    
    def _type_next_char(self):
        """显示下一个字符"""
        if not self.is_playing or self.current_index >= len(self.current_text):
            self.is_playing = False
            # 动画完成后禁用文本编辑
            self.text_widget.config(state='disabled')
            if self.callback:
                self.callback()
            return
        
        # 获取下一个字符
        char = self.current_text[self.current_index]
        
        # 播放音效
        if self.sound:
            try:
                # 停止之前可能还在播放的音效
                self.sound.stop()
                self.sound.play()
            except Exception as e:
                print(f"播放音效失败: {e}")
        
        # 插入字符
        if self.current_tag:
            self.text_widget.insert(tk.END, char, self.current_tag)
        else:
            self.text_widget.insert(tk.END, char)
        
        # 确保文本可见
        self.text_widget.see(tk.END)
        
        # 更新索引
        self.current_index += 1
        
        # 安排下一个字符的显示
        if self.is_playing:
            self.current_task = self.text_widget.after(int(self.delay * 1000), self._type_next_char)
    
    def stop(self):
        """停止动画"""
        self.is_playing = False
        if self.current_task:
            self.text_widget.after_cancel(self.current_task)
            self.current_task = None
        # 停止后禁用文本编辑
        self.text_widget.config(state='disabled')
    
    def skip(self):
        """跳过动画，直接显示完整文本"""
        self.stop()
        self.text_widget.config(state='normal')
        if self.current_tag:
            self.text_widget.insert('1.0', self.current_text, self.current_tag)
        else:
            self.text_widget.insert('1.0', self.current_text)
        self.text_widget.see(tk.END)
        self.text_widget.config(state='disabled')
        
        if self.callback:
            self.callback()

    def is_active(self):
        """检查动画是否正在播放"""
        return self.is_playing