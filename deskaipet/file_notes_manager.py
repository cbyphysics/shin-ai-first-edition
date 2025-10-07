import tkinter as tk
from tkinter import simpledialog
import os

class FileNotesManager:
    def __init__(self, pet_app):
        """
        文件注释管理器
        
        Args:
            pet_app: 主程序实例，用于访问动画和显示功能
        """
        self.pet_app = pet_app
        self.notes_file = "folder_notes.txt"
        
        # 确保注释文件存在
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                f.write("")

    def read_notes(self):
        """读取文件注释"""
        # 显示提示消息
        self.pet_app.show_message("想读的文件的名字是？", "talking1")
        
        # 延迟一下，让消息显示完成后再弹出输入框
        self.pet_app.root.after(1000, self._ask_filename_for_reading)

    def _ask_filename_for_reading(self):
        """询问要读取的文件名"""
        filename = simpledialog.askstring("读取文件注释", "请输入文件名:", parent=self.pet_app.root)
        
        if filename:
            self._read_notes_from_file(filename)
        else:
            self.pet_app.show_message("取消读取文件注释", "denying")

    def _read_notes_from_file(self, filename):
        """从文件中读取注释"""
        try:
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            notes_found = False
            for line in lines:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] == filename:
                        note = parts[1]
                        self.pet_app.show_message(f"文件 '{filename}' 的注释是:\n{note}", "talking1")
                        notes_found = True
                        break
            
            if not notes_found:
                self.pet_app.show_message(f"没有找到文件 '{filename}' 的注释", "denying")
                
        except Exception as e:
            self.pet_app.show_message(f"读取文件注释时出错:\n{str(e)}", "denying")

    def add_notes(self):
        """添加文件注释"""
        # 显示提示消息
        self.pet_app.show_message("想对于哪个文件修改注释 (y)，想新建注释 (n)", "talking1")
        
        # 延迟一下，让消息显示完成后再弹出输入框
        self.pet_app.root.after(1000, self._ask_modify_or_new)

    def _ask_modify_or_new(self):
        """询问是修改还是新建注释"""
        choice = simpledialog.askstring("添加文件注释", "请输入 y 或 n:", parent=self.pet_app.root)
        
        if choice and choice.lower() == 'y':
            self._ask_filename_for_modification()
        elif choice and choice.lower() == 'n':
            self._ask_filename_for_new_note()
        else:
            self.pet_app.show_message("已取消添加文件注释", "denying")

    def _ask_filename_for_modification(self):
        """询问要修改注释的文件名"""
        filename = simpledialog.askstring("修改文件注释", "请输入要修改注释的文件名:", parent=self.pet_app.root)
        
        if filename:
            self._ask_note_content(filename, modify=True)
        else:
            self.pet_app.show_message("已取消修改文件注释", "denying")

    def _ask_filename_for_new_note(self):
        """询问要添加注释的文件名"""
        filename = simpledialog.askstring("新建文件注释", "请输入要添加注释的文件名:", parent=self.pet_app.root)
        
        if filename:
            self._ask_note_content(filename, modify=False)
        else:
            self.pet_app.show_message("已取消新建文件注释", "denying")

    def _ask_note_content(self, filename, modify=False):
        """询问注释内容"""
        note = simpledialog.askstring("文件注释", f"请输入文件 '{filename}' 的注释:", parent=self.pet_app.root)
        
        if note:
            self._save_note_to_file(filename, note, modify)
        else:
            self.pet_app.show_message("已取消保存文件注释", "denying")

    def _save_note_to_file(self, filename, note, modify=False):
        """将注释保存到文件"""
        try:
            # 读取现有注释
            notes_dict = {}
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) >= 2:
                            notes_dict[parts[0]] = parts[1]
            
            # 更新或添加注释
            notes_dict[filename] = note
            
            # 写回文件
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                for fname, fnote in notes_dict.items():
                    f.write(f"{fname}|{fnote}\n")
            
            action = "修改" if modify else "添加"
            self.pet_app.show_message(f"成功{action}文件 '{filename}' 的注释", "talking1")
            
        except Exception as e:
            self.pet_app.show_message(f"保存文件注释时出错:\n{str(e)}", "denying")