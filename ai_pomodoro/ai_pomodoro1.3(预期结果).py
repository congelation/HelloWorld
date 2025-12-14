import time
import csv
import os
import sys
from datetime import datetime, timedelta

def play_alarmsound():
    """播放3声连续闹钟音（响亮到能穿透耳机！）"""
    if sys.platform == 'win32':
        try:
            # 优先用系统闹钟音（Windows默认闹钟）
            alarm_path = "C:\\Windows\\Media\\Alarm01.wav"
            if os.path.exists(alarm_path):
                os.system(f'start /min "" "{alarm_path}"')
            else:
                # 用高频响亮Beep（1500Hz, 500ms）
                for _ in range(3):
                    import winsound
                    winsound.Beep(1500, 500)
                    time.sleep(0.3)
        except:
            os.system('echo -n \a')
    
    elif sys.platform == 'darwin':
        try:
            # macOS用系统闹钟音
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            time.sleep(0.5)
            os.system('afplay /System/Library/Sounds/Glass.aiff')
            time.sleep(0.5)
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        except:
            os.system('say "Time up!"')
    
    else:  # Linux
        for _ in range(3):
            os.system('echo -n \a')
            time.sleep(0.3)

def pomodoro_timer():
    print("🍅 番茄钟开始！专注25分钟...")
    
    # ✅ 第一步：输入预期结果
    expected = input("\n📌 预期结果（计划要完成的目标）: ")
    if not expected.strip():
        expected = "未设定目标"
    
    # 倒计时25分钟
    for i in range(1 * 60, 0, -1):
        minutes = i // 60
        seconds = i % 60
        print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 时间到！")
    play_alarmsound()  # 播放响亮闹钟音
    
    # ✅ 第二步：输入实际结果
    actual = input("\n✅ 实际结果（实际完成的情况）: ")
    if not actual.strip():
        actual = "未完成"
    
    # 保存到CSV
    filename = "time_log.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['日期', '开始时间', '结束时间', '预期结果', '实际结果', '时长(分钟)'])
        
        now = datetime.now()
        start_time = now - timedelta(minutes=25)
        writer.writerow([
            now.strftime('%Y-%m-%d'),
            start_time.strftime('%H:%M'),
            now.strftime('%H:%M'),
            expected,
            actual,
            25
        ])
    
    print(f"\n✅ 已记录：\n  预期: {expected}\n  实际: {actual} (25分钟)")
    print(f"📊 数据已保存到 {filename}")
    print("💡 提示：下次直接运行脚本，25分钟自动提醒！")

if __name__ == "__main__":
    pomodoro_timer()