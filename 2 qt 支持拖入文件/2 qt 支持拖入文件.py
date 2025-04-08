import sys

from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QVBoxLayout, QWidget, QFileDialog, QMessageBox, QShortcut)

from CreateComponent import *

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setAcceptDrops(True)  # 启用拖放功能
        self.current_file = None

    def initUI(self):
        # 设置主窗口
        self.setWindowTitle('TXT文件拖入编辑器')
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = create_text_edit()

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        central_widget.setLayout(layout)

        # 创建快捷键
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self.save_file)



    # 拖入事件处理
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    def dropEvent(self, event):
        # 获取拖入的文件
        files = [u for u in event.mimeData().urls()]

        # 只处理第一个文件
        if files:
            filepath = files[0].toLocalFile()

            # 检查是否为TXT文件
            if filepath.lower().endswith('.txt'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.text_edit.setPlainText(content)
                        self.current_file = filepath
                        self.setWindowTitle(f'TXT编辑器 - {filepath}')
                except Exception as e:
                    QMessageBox.warning(self, '错误', f'无法打开文件: {str(e)}')
            else:
                QMessageBox.warning(self, '警告', '请拖入TXT文本文件')

    # 保存功能
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                    QMessageBox.information(self, '成功', '文件已保存')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'保存文件失败: {str(e)}')
        else:
            QMessageBox.warning(self, '警告', '没有打开的文件可供保存')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec_())
