import threading
import time
from PIL import Image, ImageTk
import os

class PetAnimation:
    def __init__(self, pet_label):
        """
        宠物动画管理器
        
        Args:
            pet_label: tkinter Label控件，用于显示宠物表情
        """
        self.pet_label = pet_label
        self.current_expression = "close"
        self.expression_frame = 2
        self.animation_active = False
        self.animation_thread = None
        self.current_animation = None
        
        # 表情图片字典
        self.expressions = {
            "open1": None,
            "close": None,  
            "open2": None,  
            "denying": None
        }
        
        # 加载表情图片
        self.load_expressions()
        
        # print("动画管理器初始化完成")
    
    def load_expressions(self):
        """
        加载表情图片
        """
        try:
            # 尝试加载图片文件
            image_paths = {
                "open1": "face1.1.1.png",     
                "close": "face1.2.1.png", 
                "open2": "face1.3.png",  
                "denying": "face1.4.png"   
            }
            
            for expr_name, file_path in image_paths.items():
                if os.path.exists(file_path):
                    image = Image.open(file_path)
                    image = image.resize((80, 80), Image.Resampling.LANCZOS)
                    self.expressions[expr_name] = ImageTk.PhotoImage(image)
                    # print(f"加载表情图片成功: {file_path}")
                else:
                    # 如果图片文件不存在，创建彩色默认图片
                    colors = {
                        "open1": "lightblue",
                        "close": "lightblue",
                        "open2": "lightblue",
                        "denying": "lightcoral"
                    }
                    image = Image.new('RGB', (80, 80), color=colors[expr_name])
                    self.expressions[expr_name] = ImageTk.PhotoImage(image)
                    print(f"创建默认表情图片: {expr_name}")
        except Exception as e:
            print(f"加载表情图片失败: {e}")
            # 创建默认的彩色图片
            colors = {
                "open1": "lightblue",
                "close": "lightblue",
                "open2": "lightblue",
                "denying": "lightcoral"
            }
            for expr_name, color in colors.items():
                image = Image.new('RGB', (80, 80), color=color)
                self.expressions[expr_name] = ImageTk.PhotoImage(image)
    
    def set_expression(self, expression):
        """设置宠物表情"""
        if expression != self.current_expression:
            self.current_expression = expression
            self.update_expression_display()
    
    def update_expression_display(self):
        """更新表情显示"""
        try:
            if self.current_expression == "talking1":
                # 说话时在1和2之间交替
                if self.expression_frame == 1:
                    self.pet_label.config(image=self.expressions["open1"])
                    self.expression_frame = 2
                else:
                    self.pet_label.config(image=self.expressions["open2"])
                    self.expression_frame = 1
            elif self.current_expression == "talking2":
                # 说话时在2和3之间交替
                if self.expression_frame == 3:
                    self.pet_label.config(image=self.expressions["open2"])
                    self.expression_frame = 2    
                else:
                    self.pet_label.config(image=self.expressions["open1"])
                    self.expression_frame = 3
            elif self.current_expression == "denying":
                # 否认时显示4
                self.pet_label.config(image=self.expressions["denying"])
            else:
                # 待机时显示2
                self.pet_label.config(image=self.expressions["close"])
                self.expression_frame = 2
        except Exception as e:
            print(f"更新表情显示失败: {e}")
    
    def stop_current_animation(self):
        """停止当前动画"""
        self.animation_active = False
        # 不再尝试加入当前线程，因为这会导致错误
    
    def play_idle_animation(self, duration=5):
        """播放待机动画"""
        def idle_animation():
            self.animation_active = True
            self.current_animation = "idle"
            
            start_time = time.time()
            while self.animation_active and (time.time() - start_time) < duration:
                self.set_expression("close")
                time.sleep(0.5)
                if not self.animation_active:
                    break
                    
            # 动画结束后回到默认状态
            if self.current_animation == "idle":
                self.set_expression("close")
                self.animation_active = False
        
        # 如果已经有动画在运行，先停止它
        self.stop_current_animation()
        
        self.animation_thread = threading.Thread(target=idle_animation, daemon=True)
        self.animation_thread.start()
        # print(f"开始播放待机动画，持续时间: {duration}秒")
        return self.animation_thread
    
    def play_talking_animation1(self, duration=3):
        """播放说话动画1"""
        def talking_animation():
            self.animation_active = True
            self.current_animation = "talking1"
            
            start_time = time.time()
            while self.animation_active and (time.time() - start_time) < duration:
                self.set_expression("talking1")
                time.sleep(0.3)
                if not self.animation_active:
                    break
                    
            # 动画结束后回到默认状态
            if self.current_animation == "talking1":
                self.set_expression("close")
                self.animation_active = False
        
        # 如果已经有动画在运行，先停止它
        self.stop_current_animation()
        
        self.animation_thread = threading.Thread(target=talking_animation, daemon=True)
        self.animation_thread.start()
        # print(f"开始播放说话动画1，持续时间: {duration}秒")
        return self.animation_thread
    
    def play_talking_animation2(self, duration=3):
        """播放说话动画2"""
        def talking_animation():
            self.animation_active = True
            self.current_animation = "talking2"
            
            start_time = time.time()
            while self.animation_active and (time.time() - start_time) < duration:
                self.set_expression("talking2")
                time.sleep(0.3)
                if not self.animation_active:
                    break
                    
            # 动画结束后回到默认状态
            if self.current_animation == "talking2":
                self.set_expression("close")
                self.animation_active = False
        
        # 如果已经有动画在运行，先停止它
        self.stop_current_animation()
        
        self.animation_thread = threading.Thread(target=talking_animation, daemon=True)
        self.animation_thread.start()
        # print(f"开始播放说话动画2，持续时间: {duration}秒")
        return self.animation_thread
    
    def play_denying_animation(self, duration=2):
        """播放否认动画"""
        def denying_animation():
            self.animation_active = True
            self.current_animation = "denying"
            
            start_time = time.time()
            while self.animation_active and (time.time() - start_time) < duration:
                self.set_expression("denying")
                time.sleep(0.1)
                if not self.animation_active:
                    break
                    
            # 动画结束后回到默认状态
            if self.current_animation == "denying":
                self.set_expression("close")
                self.animation_active = False
        
        # 如果已经有动画在运行，先停止它
        self.stop_current_animation()
        
        self.animation_thread = threading.Thread(target=denying_animation, daemon=True)
        self.animation_thread.start()
        # print(f"开始播放否认动画，持续时间: {duration}秒")
        return self.animation_thread
    
    def play_single_expression(self, expression, duration=2):
        """播放单个表情动画"""
        def single_animation():
            self.animation_active = True
            self.current_animation = expression
            
            # 设置指定表情
            self.set_expression(expression)
            
            # 保持指定时间
            start_time = time.time()
            while self.animation_active and (time.time() - start_time) < duration:
                time.sleep(0.1)
                if not self.animation_active:
                    break
            
            # 动画结束后回到默认状态
            if self.current_animation == expression:
                self.set_expression("close")
                self.animation_active = False
        
        # 如果已经有动画在运行，先停止它
        self.stop_current_animation()
        
        self.animation_thread = threading.Thread(target=single_animation, daemon=True)
        self.animation_thread.start()
        # print(f"开始播放表情动画: {expression}，持续时间: {duration}秒")
        return self.animation_thread
    
    def get_available_expressions(self):
        """获取可用的表情列表"""
        return list(self.expressions.keys())
    
    def is_animation_playing(self):
        """检查是否有动画正在播放"""
        return self.animation_active and self.animation_thread and self.animation_thread.is_alive()