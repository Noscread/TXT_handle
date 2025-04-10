import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = uic.loadUi('界面.ui')
    ui.show()
    sys.exit(app.exec())