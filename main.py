#!/usr/bin/python3
from PyQt5.QtWidgets import QApplication
import sys

from src.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()

    sys.exit(app.exec_())
