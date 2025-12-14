# ai_pomodoro.py - 超简版本
import time
import csv
import os
from datetime import datetime

def pomodoro_timer():
    print("🍅 番茄钟开始！专注25分钟...")
    
    # 倒计时25分钟
    for i in range(1 * 60, 0, -1):
        minutes = i // 60
        seconds = i % 60
        print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 时间到！")
    
    # 提示用户输入任务
    task = input("刚才25分钟你在做什么？（例如：写代码、看文档）：")
    
    if not task.strip():
        task = "未记录任务"
    
    # 保存到CSV文件
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

if __name__ == "__main__":
    from datetime import timedelta
    pomodoro_timer()