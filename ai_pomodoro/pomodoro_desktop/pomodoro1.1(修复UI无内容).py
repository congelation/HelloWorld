import sys
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QLabel, QVBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QTimer, Qt
import time
import os
import csv
from datetime import datetime

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

# 6. 创建主窗口（现在有UI了！）
window = QWidget()
window.setWindowTitle("番茄钟")
window.setWindowIcon(QIcon("icon.png"))
window.resize(300, 150)  # 设置窗口大小

# ✅ 关键修改：添加倒计时标签
time_label = QLabel("工作：25:00", window)
time_label.setStyleSheet("font-size: 24px; font-weight: bold;")
time_label.setAlignment(Qt.AlignCenter)

# ✅ 关键修改：布局管理
layout = QVBoxLayout()
layout.addWidget(time_label)
window.setLayout(layout)

# 7. 隐藏窗口（默认）
window.hide()

# 8. 显示窗口函数
def show_window():
    window.show()
    window.activateWindow()

# 9. 隐藏窗口函数
def hide_window():
    window.hide()

# 10. 闹钟声音
def play_alarm():
    try:
        QSound.play("alarm.wav")
    except:
        print("\a")

# 11. 番茄钟逻辑（现在带UI更新）
def start_pomodoro():
    # 工作25分钟
    work_time = 25 * 60
    print("🍅 工作开始！专注25分钟...")
    
    # 创建倒计时计时器
    timer = QTimer()
    remaining = work_time
    
    # 每秒更新UI
    def update_timer():
        nonlocal remaining
        remaining -= 1
        minutes = remaining // 60
        seconds = remaining % 60
        time_label.setText(f"工作：{minutes:02d}:{seconds:02d}")
        
        if remaining <= 0:
            timer.stop()
            print("\n⏰ 工作结束！")
            play_alarm()
            # 休息5分钟
            break_time = 5 * 60
            print("\n⏳ 休息开始！5分钟倒计时...")
            remaining = break_time
            
            # 休息倒计时
            def update_break():
                nonlocal remaining
                remaining -= 1
                minutes = remaining // 60
                seconds = remaining % 60
                time_label.setText(f"休息：{minutes:02d}:{seconds:02d}")
                
                if remaining <= 0:
                    timer.stop()
                    print("\n⏰ 休息结束！")
                    play_alarm()
            
            # 启动休息倒计时
            break_timer = QTimer()
            break_timer.timeout.connect(update_break)
            break_timer.start(1000)
    
    # 启动工作倒计时
    timer.timeout.connect(update_timer)
    timer.start(1000)

# 12. 连接托盘图标点击事件
tray.activated.connect(lambda reason: 
    show_window() if reason == QSystemTrayIcon.DoubleClick else None)

# 13. 启动番茄钟（点击托盘"显示"后）
def start_from_tray():
    start_pomodoro()

# 14. 连接"显示"菜单项
show_action.triggered.connect(start_from_tray)

# 15. 启动应用
if __name__ == "__main__":
    sys.exit(app.exec_())