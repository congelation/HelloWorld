import time
import csv
import os
import sys
from datetime import datetime, timedelta

def play_alarmsound():
    """播放3声连续闹钟音（响亮到能穿透耳机！）"""
    if sys.platform == 'win32':
        # Windows：用系统闹钟音效（比Beep响10倍）
        try:
            # 优先使用系统闹钟音效（常见路径）
            alarm_path = "C:\\Windows\\Media\\Alarm01.wav"
            if os.path.exists(alarm_path):
                os.system(f'start /min "" "{alarm_path}"')
            else:
                # 退而求其次：用Beep循环3次（响亮模式）
                for _ in range(3):
                    # 频率1500Hz（比默认1000Hz更刺耳）
                    # 持续500ms（比默认200ms更长）
                    import winsound
                    winsound.Beep(1500, 500)
                    time.sleep(0.3)
        except:
            # 最后兜底：用系统提示音
            os.system('echo -n \a')
    
    elif sys.platform == 'darwin':
        # macOS：用系统闹钟音效
        try:
            # 系统默认闹钟音（比say响）
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            time.sleep(0.5)
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            time.sleep(0.5)
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        except:
            os.system('say "Time up!"')
    
    else:  # Linux
        # Linux：用终端蜂鸣3次（响亮版）
        for _ in range(3):
            os.system('echo -n \a')
            time.sleep(0.3)

def pomodoro_timer():
    print("🍅 番茄钟开始！专注25分钟...")
    
    # 倒计时25分钟
    for i in range(1 * 10, 0, -1):
        minutes = i // 60
        seconds = i % 60
        print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 时间到！")
    play_alarmsound()  # 播放响亮闹钟音
    
    # 保存到CSV（无需弹窗！）
    task = input("\n刚才25分钟你在做什么？（回车默认“未记录”）: ")
    if not task.strip():
        task = "未记录任务"
    
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
    print("💡 提示：下次直接运行脚本，25分钟自动提醒！")

if __name__ == "__main__":
    pomodoro_timer()