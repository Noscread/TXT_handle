import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QToolBar, QAction, QMenu, QLabel,
                             QListWidget, QTextEdit, QStatusBar, QSplitter, QToolButton, QFileDialog, QMessageBox,
                             QSizePolicy, QDialog, QVBoxLayout, QLineEdit, QPushButton, QListWidgetItem)
import os
import json

keyword = ""

class NovelReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小说阅读器")
        self.resize(1000, 700)
        # 初始化字体设置
        self.default_font = "Arial"
        self.default_font_size = 14
        self.keyword = keyword

        # 创建主窗口的各个部件
        self.create_toolbar()
        self.create_central_widget()
        self.create_status_bar()

        # 添加成员变量来存储章节内容
        self.chapters = []
        self.chapter_titles = []  # 新增：用于存储每章的第一行文本
        self.current_chapter_index = -1

        # 添加快捷键支持
        self.setup_shortcuts()

        # 添加新的成员变量存储状态
        self.reading_history = {}  # 格式: {book_name: last_chapter_index}
        self.current_book = None  # 当前阅读的书籍

        # 应用启动时自动加载书籍
        self.load_saved_books()

        # 尝试从配置文件加载字体设置
        self.load_font_settings()

    def create_toolbar(self):
        toolbar = self.toolBar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar) # 固定位置


        # 菜单对象 和 菜单项
        file_menu = QMenu("文件", self) # 菜单对象(QMenu)
        f1_action = QAction("导入文件", self)
        f2_action = QAction("删除文件", self)
        f3_action = QAction("重新加载", self)
        file_menu.addAction(f1_action)
        file_menu.addAction(f2_action)
        file_menu.addAction(f3_action)
        # 绑定点击事件 - 方法1: 使用lambda表达式
        f1_action.triggered.connect(lambda: self.on_file_import())
        # 方法2: 直接连接到一个方法
        f2_action.triggered.connect(self.on_file_delete)
        # 方法3: 使用带参数的连接
        f3_action.triggered.connect(lambda checked: self.on_file_reload(checked))


        file_button = QToolButton(self) # 创建一个专用按钮（QToolButton）并关联菜单
        file_button.setText("文件")  # 设置按钮文字
        file_button.setMenu(file_menu) # 将之前创建的file_menu(文件菜单)设置为这个按钮的下拉菜单
        file_button.setPopupMode(QToolButton.InstantPopup)  # 点击立即弹出菜单
        toolbar.addWidget(file_button)  # 工具栏上添加一个显示"文件"文字的按钮

        tool_menu = QMenu("工具", self)
        t1_action = QAction("字体设置", self)  # 修改文本更清晰
        t2_action = QAction("关键词搜索", self)  # 修改工具2的名称为"关键词搜索"
        t3_action = QAction("工具3", self)
        tool_menu.addAction(t1_action)
        tool_menu.addAction(t2_action)
        tool_menu.addAction(t3_action)
        # 连接字体设置功能
        t1_action.triggered.connect(self.show_font_dialog)
        # 连接到新的关键词搜索功能
        t2_action.triggered.connect(self.show_keyword_search_dialog)

        tool_button = QToolButton(self)
        tool_button.setText("工具")
        tool_button.setMenu(tool_menu)
        tool_button.setPopupMode(QToolButton.InstantPopup)
        toolbar.addWidget(tool_button)
    def create_central_widget(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget) # 横向排列子部件 layout -> widget
        main_layout.setContentsMargins(0, 0, 0, 0) # 将布局的边距设为 0（移除默认的内边距），使内容紧贴窗口边缘
        splitter = QSplitter(Qt.Horizontal) # 一个可拖动的分割器，允许用户动态调整子部件的宽度/高度

        # 1. 左侧书架
        self.bookshelf = QListWidget()
        self.bookshelf.setMinimumWidth(100)
        self.bookshelf.setMaximumWidth(500)
        self.bookshelf.itemClicked.connect(self.on_book_selected)
        self.bookshelf.setStyleSheet("background-color: #f5f5f5;")
        self.bookshelf.addItems([

        ])

        # 2. 中间目录
        self.toc = QListWidget()
        self.toc.setMinimumWidth(150)
        self.toc.setMaximumWidth(500)
        self.toc.itemClicked.connect(self.on_chapter_selected)
        self.toc.setStyleSheet("background-color: #e0e0e0;")
        self.toc.addItems([
            "第一章 请",
            "第二章 选",
            "第三章 择",
            "第四章 书",
            "第五章 籍"
        ])

        # 3. 右侧内容区域
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setStyleSheet("font-size: 14px;")
        self.content.setText("""第一章 提醒

        请选择书籍，这里才会显示小说内容。

        """)

        # 添加部件到分割器
        splitter.addWidget(self.bookshelf)
        splitter.addWidget(self.toc)
        splitter.addWidget(self.content)

        # 设置分割器初始比例
        splitter.setSizes([150, 200, 650])

        # 将分割器添加到主布局
        main_layout.addWidget(splitter) # layout -> splitter

    def create_status_bar(self):
        # 创建状态栏
        self.statusBar = QStatusBar()  # 创建一个 状态栏对象
        self.setStatusBar(self.statusBar)  # 将创建的状态栏对象 绑定到主窗口（QMainWindow）

        # 左半部分 - 阅读进度
        self.progress_label = QLabel("阅读进度: 12% (第5章第3节)")
        self.progress_label.setStyleSheet("padding-left: 5px;")
        self.progress_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 新增：设置左对齐并垂直居中

        # 右半部分 - 用于将按钮推到右侧的空格部件
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # 书架构件按钮
        self.bookshelf_btn = QToolButton()
        self.bookshelf_btn.setText("书架: 展开")
        self.bookshelf_btn.setCheckable(True)
        self.bookshelf_btn.setChecked(True)
        self.bookshelf_btn.clicked.connect(self.toggle_bookshelf)

        # 目录构件按钮
        self.toc_btn = QToolButton()
        self.toc_btn.setText("目录: 展开")
        self.toc_btn.setCheckable(True)
        self.toc_btn.setChecked(True)
        self.toc_btn.clicked.connect(self.toggle_toc)

        # 内容构件按钮
        self.content_btn = QToolButton()
        self.content_btn.setText("内容: 展开")
        self.content_btn.setCheckable(True)
        self.content_btn.setChecked(True)
        self.content_btn.clicked.connect(self.toggle_content)

        # 添加到状态栏
        self.statusBar.addPermanentWidget(self.progress_label)  # 左侧标签
        self.statusBar.addPermanentWidget(spacer)  # 弹性空间
        self.statusBar.addPermanentWidget(self.bookshelf_btn)  # 按钮1
        self.statusBar.addPermanentWidget(self.toc_btn)  # 按钮2
        self.statusBar.addPermanentWidget(self.content_btn)  # 按钮3

    def show_keyword_search_dialog(self):
        """显示关键词搜索对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("关键词搜索")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout()

        # 关键词输入区域
        keyword_label = QLabel("输入关键词（用逗号或空格分隔）:")
        self.keyword_input = QLineEdit()
        self.keyword_input.setText(self.keyword)  # 设置默认值为"战斗"
        layout.addWidget(keyword_label)
        layout.addWidget(self.keyword_input)

        # 按钮区域
        button_layout = QHBoxLayout()
        search_button = QPushButton("搜索")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(search_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # 连接信号
        search_button.clicked.connect(lambda: self.do_keyword_search(dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.exec_()

    def do_keyword_search(self, dialog):
        """执行关键词搜索"""
        # 获取用户输入的关键词，如果没有输入则使用默认值"战斗"
        input_text = self.keyword_input.text().strip()
        if not input_text:
            input_text = self.keyword # 设置默认关键词

        # 处理输入，分割关键词
        keywords = []
        for word in input_text.replace(",", " ").split():
            word = word.strip()
            if word:  # 确保不是空字符串
                keywords.append(word)

        if not keywords:
            QMessageBox.warning(self, "警告", "没有有效的关键词")
            return

        # 搜索各章节中的关键词出现次数
        print(f"搜索关键词: {keywords}")

        # 确保有章节内容
        if not self.chapters:
            QMessageBox.warning(self, "警告", "没有可搜索的章节内容")
            return

        # 搜索每个章节的关键词
        keyword_counts = {}  # {chapter_index: count}
        for i, chapter in enumerate(self.chapters):
            total = 0
            for keyword in keywords:
                total += chapter.count(keyword)
            keyword_counts[i] = total

        # 更新目录显示关键词计数
        self.update_toc_with_keyword_counts(keyword_counts)

        dialog.accept()

    def update_toc_with_keyword_counts(self, keyword_counts):
        """在目录项右侧显示关键词数量"""
        self.toc.clear()

        for i, title in enumerate(self.chapter_titles):
            count = keyword_counts.get(i, 0)
            item = QListWidgetItem(f"{title} ({count})" if count > 0 else title)
            self.toc.addItem(item)

        # 恢复当前选中的章节
        if 0 <= self.current_chapter_index < len(self.chapter_titles):
            self.toc.setCurrentRow(self.current_chapter_index)

    def show_font_dialog(self):
        """显示字体设置对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QHBoxLayout
        from PyQt5.QtGui import QFontDatabase

        dialog = QDialog(self)
        dialog.setWindowTitle("字体设置")
        layout = QVBoxLayout()

        # 字体选择
        font_label = QLabel("选择字体:")
        font_combo = QComboBox()
        font_db = QFontDatabase()
        font_combo.addItems(font_db.families())
        layout.addWidget(font_label)
        layout.addWidget(font_combo)

        # 字体大小
        size_label = QLabel("字体大小:")
        size_spin = QSpinBox()
        size_spin.setRange(8, 72)  # 设置字体大小范围
        size_spin.setValue(14)  # 默认值
        layout.addWidget(size_label)
        layout.addWidget(size_spin)

        # 按钮区域
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # 设置当前值
        current_font = self.content.font()
        font_combo.setCurrentText(current_font.family())
        size_spin.setValue(current_font.pointSize())

        # 连接信号
        def apply_font():
            font = font_combo.currentText()
            size = size_spin.value()
            self.content.setStyleSheet(f"font-family: '{font}'; font-size: {size}pt;")
            self.save_font_settings()  # 保存字体设置
            dialog.accept()

        ok_button.clicked.connect(apply_font)
        cancel_button.clicked.connect(dialog.reject)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_font_settings(self):
        """保存当前字体设置到配置文件"""
        font_settings = {
            'font_family': self.content.font().family(),
            'font_size': self.content.font().pointSize()
        }

        # 确保books目录存在
        os.makedirs("books", exist_ok=True)

        with open("books/font_settings.json", "w", encoding="utf-8") as f:
            json.dump(font_settings, f)

    def load_font_settings(self):
        """从配置文件加载字体设置"""
        font_file = "books/font_settings.json"
        if os.path.exists(font_file):
            try:
                with open(font_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    font_family = settings.get('font_family', self.default_font)
                    font_size = settings.get('font_size', self.default_font_size)

                    # 应用加载的字体设置
                    self.content.setStyleSheet(
                        f"font-family: '{font_family}'; font-size: {font_size}pt;"
                    )
            except:
                # 如果加载失败，使用默认设置
                self.content.setStyleSheet(
                    f"font-family: '{self.default_font}'; font-size: {self.default_font_size}px;"
                )
        else:
            # 如果文件不存在，使用默认设置
            self.content.setStyleSheet(
                f"font-family: '{self.default_font}'; font-size: {self.default_font_size}px;"
            )

    def toggle_bookshelf(self):
        """切换书架显示状态"""
        is_visible = not self.bookshelf.isHidden()
        self.bookshelf.setHidden(is_visible)
        self.bookshelf_btn.setText(f"书架: {'展开' if is_visible else '隐藏'}")
        self.bookshelf_btn.setChecked(not is_visible)

    def toggle_toc(self):
        """切换目录显示状态"""
        is_visible = not self.toc.isHidden()
        self.toc.setHidden(is_visible)
        self.toc_btn.setText(f"目录: {'展开' if is_visible else '隐藏'}")
        self.toc_btn.setChecked(not is_visible)

    def toggle_content(self):
        """切换内容显示状态"""
        is_visible = not self.content.isHidden()
        self.content.setHidden(is_visible)
        self.content_btn.setText(f"内容: {'展开' if is_visible else '隐藏'}")
        self.content_btn.setChecked(not is_visible)
    def setup_shortcuts(self):
        # 添加快捷键（上一章/下一章）
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtWidgets import QShortcut

        self.prev_chapter_shortcut = QShortcut(QKeySequence("Left"), self)
        self.prev_chapter_shortcut.activated.connect(self.prev_chapter)

        self.next_chapter_shortcut = QShortcut(QKeySequence("Right"), self)
        self.next_chapter_shortcut.activated.connect(self.next_chapter)

    def load_saved_books(self):
        """从books文件夹加载所有书籍"""
        # 确保books目录存在
        os.makedirs("books", exist_ok=True)

        # 加载所有txt文件
        for filename in os.listdir("books"):
            if filename.endswith(".txt"):
                self.bookshelf.addItem(filename)

        # 如果有历史记录文件，加载阅读进度
        if os.path.exists("books/reading_history.json"):
            with open("books/reading_history.json", "r", encoding="utf-8") as f:
                self.reading_history = json.load(f)


    def save_reading_progress(self):
        """保存当前的阅读进度到文件"""
        if self.current_book and self.current_chapter_index >= 0:
            self.reading_history[self.current_book] = self.current_chapter_index

        with open("books/reading_history.json", "w", encoding="utf-8") as f:
            json.dump(self.reading_history, f, ensure_ascii=False, indent=2)

    def load_novel_from_file(self, file_path):
        """从文件加载小说内容并解析章节"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.parse_chapters(content)

                # 更新书架栏，显示导入的书籍名（不带路径）
                book_name = os.path.basename(file_path)
                self.bookshelf.addItem(book_name)

                # 确保books目录存在
                os.makedirs("books", exist_ok=True)

                # 将文件复制到books目录
                target_path = os.path.join("books", book_name)
                if not os.path.exists(target_path):
                    with open(target_path, 'w', encoding='utf-8') as target_file:
                        target_file.write(content)

                # 更新目录列表
                self.toc.clear()
                self.toc.addItems(self.chapter_titles)

                # 显示第一章
                if self.chapters:
                    self.current_chapter_index = 0
                    self.display_chapter(self.current_chapter_index)

                # 更新当前书籍
                book_name = os.path.basename(file_path)
                self.current_book = book_name

                # 如果这本书有阅读记录，跳转到对应章节
                if book_name in self.reading_history:
                    last_chapter = self.reading_history[book_name]
                    if last_chapter < len(self.chapters):
                        self.display_chapter(last_chapter)
                elif self.chapters:  # 否则显示第一章
                    self.display_chapter(0)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")

    def parse_chapters(self, content):
        """解析文本内容为章节，将第一章之前的内容作为前言"""
        self.chapters = []
        self.chapter_titles = []  # 清空标题数组
        lines = content.split('\n')
        current_chapter = []
        has_found_first_chapter = False  # 标记是否找到第一章
        preface_lines = []  # 存储前言内容

        for line in lines:
            line = line.strip()  # 去除首尾空白
            if not line:  # 跳过空行
                continue

            # 判断是否是章节行 - 更灵活的匹配规则
            is_chapter_line = (line.startswith('第') and
                               any(marker in line for marker in ['章', '回', '节', '篇', '卷', '部']) and
                               any(char in line for char in
                                   ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '0',
                                    '1', '2', '3', '4', '5', '6', '7', '8', '9']))

            if is_chapter_line:
                # 如果是第一次找到章节行
                if not has_found_first_chapter:
                    # 将前面收集的内容作为前言
                    if preface_lines:
                        self.chapters.append('\n'.join(preface_lines))
                        self.chapter_titles.append("前言")
                    has_found_first_chapter = True

                # 处理当前章节
                if current_chapter:
                    self.chapters.append('\n'.join(current_chapter))
                    current_chapter = []
                self.chapter_titles.append(line)

            # 将行内容添加到适当的位置
            if has_found_first_chapter:
                current_chapter.append(line)
            else:
                preface_lines.append(line)

        # 处理最后一章
        if current_chapter:
            self.chapters.append('\n'.join(current_chapter))

        # 如果没有找到任何章节，则将全部内容作为前言
        if not has_found_first_chapter and preface_lines:
            self.chapters.append('\n'.join(preface_lines))
            self.chapter_titles.append("前言")

    def display_chapter(self, index):
        """显示指定章节的内容"""
        if 0 <= index < len(self.chapters):
            self.current_chapter_index = index
            self.content.setText(self.chapters[index])
            self.toc.setCurrentRow(index)

            # 安全获取章节标题
            chapter_title = ""
            if index < len(self.chapter_titles) and self.chapter_titles[index]:
                chapter_title = self.chapter_titles[index]

            # 计算阅读进度（1-based）
            total_chapters = len(self.chapters)
            if total_chapters > 0:
                progress = int((index + 1) / total_chapters * 100)
                status_msg = f"阅读进度: {progress}% ({chapter_title}, 共{total_chapters}章)"
                self.progress_label.setText(status_msg)

    def on_book_selected(self, item):
        """处理书架书籍被选中的事件"""
        if not item:
            return  # 如果没有选中任何书籍则直接返回

        # 先保存当前书籍的阅读进度（如果有）
        if self.current_book is not None and self.current_chapter_index >= 0:
            self.reading_history[self.current_book] = self.current_chapter_index
            self.save_reading_progress()

        # 加载新选择的书籍
        book_name = item.text()
        self.current_book = book_name  # 记录当前书籍
        self.read_current_novel(book_name)

        # 恢复新书籍的阅读进度
        if book_name in self.reading_history:
            last_chapter = self.reading_history[book_name]
            if last_chapter < len(self.chapters):
                self.display_chapter(last_chapter)
        else:
            # 如果没有记录，显示第一章
            self.display_chapter(0)

    def read_current_novel(self, book_name):
        """读取并显示当前选中的书籍内容"""
        try:
            # 从books目录加载文件
            file_path = os.path.join("books", book_name)
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "警告", f"找不到书籍文件: {book_name}")
                return

            # 读取文件内容并解析章节
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.parse_chapters(content)

            # 更新目录列表，使用章节标题
            self.toc.clear()
            self.toc.addItems(self.chapter_titles)  # 使用章节第一行文本作为标题

            # 显示第一章
            if self.chapters:
                self.current_chapter_index = 0
                self.display_chapter(self.current_chapter_index)
            # 更新状态栏显示当前阅读的书籍
            self.statusBar.showMessage(f"当前阅读: {book_name}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载书籍失败: {str(e)}")

    def on_chapter_selected(self, item):
        """目录章节被点击时的处理"""
        if not item:
            return  # 如果没有选中项则直接返回

        try:
            index = self.toc.row(item)
            if 0 <= index < len(self.chapters):  # 检查索引是否有效
                self.display_chapter(index)
            else:
                QMessageBox.warning(self, "警告", "章节索引无效")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载章节时出错: {str(e)}")

    def prev_chapter(self):
        """切换到上一章"""
        if self.chapters and self.current_chapter_index > 0:
            self.display_chapter(self.current_chapter_index - 1)

    def next_chapter(self):
        """切换到下一章"""
        if self.chapters and self.current_chapter_index < len(self.chapters) - 1:
            self.display_chapter(self.current_chapter_index + 1)

    def on_file_import(self):
        """导入文件操作"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择小说文件", "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            self.load_novel_from_file(file_path)

        print("导入文件被点击")

    def on_file_delete(self):
        """删除当前加载的小说"""
        self.chapters = []
        self.current_chapter_index = -1
        self.toc.clear()
        content = self.findChild(QTextEdit)
        content.setText("请选择书籍，这里才会显示小说内容。")
        self.statusBar.showMessage("")

        print("删除文件被点击")

    def on_file_reload(self, checked):
        print(f"重新加载被点击，checked参数值: {checked}")

    def closeEvent(self, event):
        """窗口关闭时自动保存进度"""
        self.save_reading_progress()
        self.save_font_settings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = NovelReader()
    reader.show()
    sys.exit(app.exec_())