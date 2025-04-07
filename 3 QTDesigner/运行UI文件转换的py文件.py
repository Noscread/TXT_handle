import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow

from 界面UI import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 创建 UI 对象
        self.ui = Ui_MainWindow()
        # 调用 setupUi 方法设置 UI
        self.ui.setupUi(self)


if __name__ == "__main__":
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    # 创建主窗口实例
    window = MainWindow()
    # 显示主窗口
    window.show()
    # 启动应用程序的事件循环
    sys.exit(app.exec())