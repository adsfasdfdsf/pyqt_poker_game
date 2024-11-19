import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from poker_client import Ui_MainWindow


class PokerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PokerApp()
    ex.show()
    sys.exit(app.exec())