import json
import sys
from PIL import Image

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from poker_client import Ui_MainWindow
from PyQt6 import QtCore
from card import Card, suits, Suit, to_suits, State
from PyQt6.QtNetwork import QTcpSocket


def string_from_byte(n):
    return str(n.data())[2:-1]


def make_table(my_cards, deck):
    image = Image.open("./img/poker_table.png")

    unknown = Image.open("./img/unknown.png")
    card_width, card_height = unknown.size

    x, y = image.size

    if len(my_cards):
        first, second = my_cards
        card1 = Image.open(f"./img/deck/{suits[first.suit]}/card_{first.value}.png")
        card2 = Image.open(f"./img/deck/{suits[second.suit]}/card_{second.value}.png")
        image.paste(card1, ((x // 2) - card_width - 5, (y // 6) * 4))
        image.paste(card2, ((x // 2) + 5, (y // 6) * 4))
    else:
        image.paste(unknown, ((x // 2) - card_width - 5, (y // 6) * 4))
        image.paste(unknown, ((x // 2) + 5, (y // 6) * 4))
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
        self.hand = []
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.on_connected)
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.connectToHost("127.0.0.1", 50051)
        self.name = ""
        self.balance = 0
        self.opp = State.No

    def set_name(self, name):
        self.name = name

    def set_cards(self, data):
        self.hand = [Card(to_suits[data[0]["suit"]], data[0]["value"]), Card(to_suits[data[1]["suit"]], data[1]["value"])]

    def set_community_cards(self, data):
        pass

    def on_ready_read(self):
        msg = self.sender().readAll()
        print(string_from_byte(msg))
        coms = json.loads(string_from_byte(msg))
        print(coms)
        for data in coms:
            if data["command"] == "set_name":
                self.set_name(data["name"])
            elif data["command"] == "set_cards":
                self.set_cards(data["cards"])
            elif data["command"] == "set_balance":
                self.balance = int(data["value"])
            elif data["command"] == "set_community_cards":
                self.set_community_cards(data)
            elif data["command"] == "set_opp":
                if data["state"] == "Call":
                    self.opp = State.Call
                self.enable_buttons()

        self.update_background()

    def on_connected(self):
        print("smthing")

    @QtCore.pyqtSlot()
    def on_pass_button_clicked(self):
        msg = {}
        msg["name"] = self.name
        msg["command"] = "Pass"
        self.write(json.dumps([msg]))
        self.update_background()
        self.disable_buttons()


    def enable_buttons(self):
        self.raise_button.setDisabled(False)
        self.check_button.setDisabled(False)
        self.call_button.setDisabled(False)
        self.pass_button.setDisabled(False)


    def disable_buttons(self):
        self.raise_button.setDisabled(True)
        self.check_button.setDisabled(True)
        self.call_button.setDisabled(True)
        self.pass_button.setDisabled(True)

    @QtCore.pyqtSlot()
    def on_check_button_clicked(self):
        msg = {}
        msg["name"] = self.name
        msg["command"] = "Check"
        self.write(json.dumps([msg]))
        print("check clicked")
        self.disable_buttons()

    @QtCore.pyqtSlot()
    def on_raise_button_clicked(self):
        msg = {}
        msg["name"] = self.name
        msg["command"] = "Check"
        msg["value"] = self.slider_value
        self.write(json.dumps([msg]))
        print(f"raise {self.slider_value} clicked")
        self.disable_buttons()

    @QtCore.pyqtSlot()
    def on_call_button_clicked(self):
        msg = {}
        msg["name"] = self.name
        msg["command"] = "Call"
        self.write(json.dumps([msg]))
        print("call clicked")
        self.disable_buttons()

    def update_background(self):
        make_table(self.hand, self.deck)
        self.table_pixmap.setPixmap(QPixmap.fromImage(QImage("./img/current_table.png")))

    def write(self, text):
        self.socket.write(str.encode(text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PokerApp()
    ex.show()
    sys.exit(app.exec())