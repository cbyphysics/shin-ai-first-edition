import time


def reminder_loop(self):
    # 每1.5小时提醒保存文件
    reminder_interval = 1.5 * 60 * 60  # 1.5小时转换为秒
    
    while True:
        time.sleep(reminder_interval)
        # 提醒时显示说话动画
        self.start_talking_animation(3)
        self.show_message("提醒：请保存您的工作文件！")