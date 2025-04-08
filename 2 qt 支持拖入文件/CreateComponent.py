from PyQt5.QtGui import QFont, QTextBlockFormat
from PyQt5.QtWidgets import QTextEdit


def create_text_edit():
    """创建一个文本内容组件"""
    # 创建文本编辑区域
    text_edit = QTextEdit()
    text_edit.setAcceptDrops(False)  # 禁止文本编辑框单独接受拖放

    # 创建一个 QFont 对象并设置字体和大小
    font = QFont()
    font.setFamily("微软雅黑")
    font.setPointSize(13)
    # 将字体应用到 QTextEdit 控件
    text_edit.setFont(font)

    return text_edit