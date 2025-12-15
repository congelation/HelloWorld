import time
import csv
import os
import sys
from datetime import datetime, timedelta

def play_alarmsound():
    """播放3声连续闹钟音（响亮到能穿透耳机！）"""
    if sys.platform == 'win32':
        try:
            alarm_path = "C:\\Windows\\Media\\Alarm01.wav"
            if os.path.exists(alarm_path):
                os.system(f'start /min "" "{alarm_path}"')
            else:
                for _ in range(3):
                    import winsound
                    winsound.Beep(1500, 500)
                    time.sleep(0.3)
        except:
            os.system('echo -n \a')
    
    elif sys.platform == 'darwin':
        try:
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
    print("🍅 番茄钟启动！工作25分钟 + 休息5分钟循环")
    print("📌 每轮：先输入目标 → 工作25分钟 → 输入结果 → 休息5分钟")
    print("="*50)
    
    while True:
        # ✅ 输入预期结果
        expected = input("\n📌 预期结果: ").strip()
        if not expected:
            expected = "未设定目标"
        
        # ✅ 工作25分钟倒计时
        print("\n🍅 工作开始！专注25分钟...")
        for i in range(25 * 60, 0, -1):
            minutes = i // 60
            seconds = i % 60
            print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
            time.sleep(1)
        
        print("\n⏰ 工作结束！")
        play_alarmsound()
        
        # ✅ 输入实际结果
        actual = input("\n✅ 实际结果: ").strip()
        if not actual:
            actual = "未完成"
        
        # ✅ 保存到CSV
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
        
        # ✅ 5分钟休息倒计时
        print("\n⏳ 休息开始！5分钟倒计时...")
        for i in range(5 * 60, 0, -1):
            minutes = i // 60
            seconds = i % 60
            print(f"\r剩余时间: {minutes:02d}:{seconds:02d}", end="")
            time.sleep(1)
        
        print("\n⏰ 休息结束！")
        play_alarmsound()
        
        # ✅ 极简输入确认
        choice = input("\n继续下一轮？(y/n): ").strip().lower()
        if choice != 'y':
            print("\n💡 感谢使用番茄钟！已退出程序。")
            break
    
    print("\n✨ 今日目标达成率：")
    print("（如需详细报告，可运行generate_report.py）")

if __name__ == "__main__":
    pomodoro_timer()