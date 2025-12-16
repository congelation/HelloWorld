import sys
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QAction, QWidget)
# 修正后的导入方式
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound  # ✅ 正确模块
from PyQt5.QtCore import QTimer, Qt

# 1. 创建应用实例
app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)  # 保持应用在后台运行

# 2. 创建系统托盘图标
tray = QSystemTrayIcon()
tray.setIcon(QIcon("icon.png"))
tray.setToolTip("番茄钟 - 工作25分钟 + 休息5分钟")

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
tray.show()

# 6. 创建主窗口（隐藏状态）
window = QWidget()
window.setWindowTitle("番茄钟")
window.setWindowIcon(QIcon("icon.png"))
window.hide()  # 默认隐藏

# 7. 显示窗口函数
def show_window():
    window.show()
    window.activateWindow()

# 8. 隐藏窗口函数
def hide_window():
    window.hide()

# 9. 闹钟声音
def play_alarm():
    # 优先用QSound播放（跨平台）
    try:
        QSound.play("alarm.wav")
    except:
        # 备用方案：用系统提示音
        print("\a")

# 10. 番茄钟逻辑
def start_pomodoro():
    # 工作25分钟
    print("🍅 工作开始！专注25分钟...")
    for i in range(25 * 60, 0, -1):
        print(f"\r剩余时间: {i//60:02d}:{i%60:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 工作结束！")
    play_alarm()
    
    # 休息5分钟
    print("\n⏳ 休息开始！5分钟倒计时...")
    for i in range(5 * 60, 0, -1):
        print(f"\r剩余时间: {i//60:02d}:{i%60:02d}", end="")
        time.sleep(1)
    
    print("\n⏰ 休息结束！")
    play_alarm()

# 11. 启动番茄钟（点击托盘菜单的"显示"后）
def start_from_tray():
    start_pomodoro()

# 12. 连接托盘图标点击事件
tray.activated.connect(lambda reason: 
    show_window() if reason == QSystemTrayIcon.DoubleClick else None)

# 13. 启动应用
if __name__ == "__main__":
    # 启动番茄钟（在托盘图标上右键点击"显示"后开始）
    sys.exit(app.exec_())