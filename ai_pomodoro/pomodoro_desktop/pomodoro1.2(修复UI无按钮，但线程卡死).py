import sys
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QLabel, QVBoxLayout, QPushButton, QInputDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QTimer, Qt
import time
import os
import csv
from datetime import datetime, timedelta

# 1. 创建应用实例
app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

# 2. 创建系统托盘图标
tray = QSystemTrayIcon()
tray.setIcon(QIcon("icon.png"))
tray.setToolTip("番茄钟 - 工作25分钟 + 休息5分钟")
tray.show()

# 3. 创建托盘菜单
menu = QMenu()
show_action = menu.addAction("显示")
hide_action = menu.addAction("隐藏")
quit_action = menu.addAction("退出")

# 4. 连接菜单事件
show_action.triggered.connect(lambda: show_window())
hide_action.triggered.connect(lambda: hide_window())
quit_action.triggered.connect(app.quit)

# 5. 设置托盘菜单
tray.setContextMenu(menu)

# 6. 创建主窗口
window = QWidget()
window.setWindowTitle("番茄钟")
window.setWindowIcon(QIcon("icon.png"))
window.resize(300, 200)
window.setWindowFlags(Qt.WindowStaysOnTopHint)

# ✅ 关键修复：先定义核心函数
def update_timer(timer, remaining, mode):
    remaining -= 1
    minutes = remaining // 60
    seconds = remaining % 60
    time_label.setText(f"{mode}: {minutes:02d}:{seconds:02d}")
    
    if remaining <= 0:
        timer.stop()

def save_to_csv(expected, actual, duration):
    filename = "time_log.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['日期', '开始时间', '结束时间', '预期结果', '实际结果', '时长(分钟)'])
        
        now = datetime.now()
        start_time = now - timedelta(minutes=duration)
        writer.writerow([
            now.strftime('%Y-%m-%d'),
            start_time.strftime('%H:%M'),
            now.strftime('%H:%M'),
            expected,
            actual,
            duration
        ])

def start_pomodoro():
    # ✅ 修复：用QInputDialog代替input()
    expected, ok = QInputDialog.getText(window, "输入目标", "请输入预期结果:")
    if not ok or not expected.strip():
        expected = "未设定目标"
    
    print(f"\n🍅 工作开始！目标: {expected}")
    work_time = 25 * 60
    remaining = work_time
    
    time_label.setText(f"工作: {remaining//60:02d}:{remaining%60:02d}")
    
    work_timer = QTimer()
    work_timer.timeout.connect(lambda: update_timer(work_timer, remaining, "工作"))
    work_timer.start(1000)
    
    def work_finished():
        work_timer.stop()
        print("\n⏰ 工作结束！")
        play_alarm()
        
        # ✅ 修复：用QInputDialog代替input()
        actual, ok = QInputDialog.getText(window, "输入结果", "请输入实际结果:")
        if not ok or not actual.strip():
            actual = "未完成"
        
        save_to_csv(expected, actual, 25)
        
        print("\n⏳ 休息开始！5分钟倒计时...")
        break_time = 5 * 60
        remaining = break_time
        time_label.setText(f"休息: {remaining//60:02d}:{remaining%60:02d}")
        
        break_timer = QTimer()
        break_timer.timeout.connect(lambda: update_timer(break_timer, remaining, "休息"))
        break_timer.start(1000)
        
        def break_finished():
            break_timer.stop()
            print("\n⏰ 休息结束！")
            play_alarm()
            
            choice, ok = QInputDialog.getItem(window, "继续？", "继续下一轮？", ["是", "否"], 0, False)
            if ok and choice == "是":
                start_pomodoro()
            else:
                print("\n💡 感谢使用番茄钟！已退出程序。")
        
        break_timer.timeout.connect(break_finished)
    
    work_timer.timeout.connect(work_finished)

# ✅ 关键修复：现在创建UI元素
time_label = QLabel("等待开始", window)
time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
time_label.setAlignment(Qt.AlignCenter)

start_button = QPushButton("开始", window)
start_button.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 8px 20px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
""")
start_button.clicked.connect(start_pomodoro)

layout = QVBoxLayout()
layout.addWidget(time_label)
layout.addWidget(start_button)
window.setLayout(layout)

# 7. 隐藏窗口（默认）
window.hide()

def show_window():
    window.show()
    window.activateWindow()

def hide_window():
    window.hide()

def play_alarm():
    try:
        QSound.play("alarm.wav")
    except:
        print("\a")

tray.activated.connect(lambda reason: 
    show_window() if reason == QSystemTrayIcon.DoubleClick else None)

if __name__ == "__main__":
    sys.exit(app.exec_())