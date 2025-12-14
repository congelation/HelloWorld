import time
import csv
import os
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime, timedelta
import sys

def play_system_bell():
    """播放系统提示音（跨平台兼容）"""
    if sys.platform == 'darwin':  # macOS
        os.system('say "Time up!"')
    elif sys.platform == 'win32':  # Windows
        import winsound
        winsound.Beep(1000, 200)  # 频率1000Hz，持续200ms
    else:  # Linux
        os.system('echo -n \a')  # 发出终端蜂鸣

def pomodoro_timer():
    print("🍅 番茄钟开始！专注25分钟...")
    
    # 倒计时25分钟
    for i in range(1 * 60, 0, -1):
        minutes = i // 60
        seconds = i % 60
        print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 时间到！")
    play_system_bell()  # 播放系统提示音
    
    # 创建弹窗（终端友好版）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    task = simpledialog.askstring(
        "任务记录", 
        "刚才25分钟你在做什么？\n(例如：写代码、看文档、开会)",
        initialvalue="未记录"
    )
    
    # 处理用户输入
    if not task or task.strip() == "":
        task = "未记录任务"
    
    # 保存到CSV
    filename = "time_log.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['日期', '开始时间', '结束时间', '任务', '时长(分钟)'])
        
        now = datetime.now()
        start_time = now - timedelta(minutes=25)
        writer.writerow([
            now.strftime('%Y-%m-%d'),
            start_time.strftime('%H:%M'),
            now.strftime('%H:%M'),
            task,
            25
        ])
    
    print(f"✅ 已记录：{task} (25分钟)")
    print(f"📊 数据已保存到 {filename}")
    print("💡 提示：下次使用直接运行脚本即可，无需手动输入！")

if __name__ == "__main__":
    pomodoro_timer()