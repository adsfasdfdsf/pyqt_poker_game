import json
import sys
from PIL import Image

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from poker_client import Ui_MainWindow
from PyQt6 import QtCore
from card import Card, suits
from PyQt6.QtNetwork import QTcpSocket


def make_table(my_cards, deck):
    image = Image.open("./img/poker_table.png")
    first, second = my_cards
    card1 = Image.open(f"./img/deck/{suits[first.suit]}/card_{first.value}.png")
    card2 = Image.open(f"./img/deck/{suits[second.suit]}/card_{second.value}.png")
    unknown = Image.open("./img/unknown.png")
    card_width, card_height = unknown.size
    x, y = image.size
    image.paste(card1, ((x // 2) - card_width - 5, (y // 6) * 4))
    image.paste(card2, ((x // 2) + 5, (y // 6) * 4))

    image.paste(unknown, ((x // 2) - card_width - 5, 0))
    image.paste(unknown, ((x // 2) + 5, 0))

    cards = len(deck)

    for i in range(cards):
        cur = Image.open(f"./img/deck/{suits[deck[i].suit]}/card_{deck[1].value}.png")
        image.paste(cur, ((x // 5) + (x // 8) * i, y // 3))

    for i in range(cards, 5):
        image.paste(unknown, ((x // 5) + (x // 8) * i, y // 3))

    image.save(f"./img/current_table.png")


class PokerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.deck = []
        self.hand = [Card("Diamonds", 4), Card("Diamonds", 6)]
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.on_connected)
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.connectToHost("127.0.0.1", 50051)


    def on_ready_read(self):
        msg = self.sender().readAll()
        data = json.loads(msg)
        #TODO handle commands

        self.update_background()

    def on_connected(self):
        print("smthing")
        self.socket.write(str.encode("slafdf;a"))

    @QtCore.pyqtSlot()
    def on_pass_button_clicked(self):
        print("button clicked")
        self.update_background()

    @QtCore.pyqtSlot()
    def on_check_button_clicked(self):
        print("check clicked")

    @QtCore.pyqtSlot()
    def on_raise_button_clicked(self):
        print(f"raise {self.slider_value} clicked")

    @QtCore.pyqtSlot()
    def on_call_button_clicked(self):
        print("call clicked")

    def update_background(self):
        make_table(self.hand, self.deck)
        self.table_pixmap.setPixmap(QPixmap.fromImage(QImage("./img/current_table.png")))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PokerApp()
    ex.show()
    sys.exit(app.exec())