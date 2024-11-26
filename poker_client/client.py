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
    card1 = unknown
    card2 = unknown
    if len(my_cards):
        first, second = my_cards
        card1 = Image.open(f"./img/deck/{suits[first.suit]}/card_{first.value}.png")
        card2 = Image.open(f"./img/deck/{suits[second.suit]}/card_{second.value}.png")

    image.paste(card1, ((x // 2) - card_width - 5, (y // 6) * 4))
    image.paste(card2, ((x // 2) + 5, (y // 6) * 4))


    image.paste(unknown, ((x // 2) - card_width - 5, 10))
    image.paste(unknown, ((x // 2) + 5, 10))



    cards = len(deck)
    for i in range(cards):
        cur = Image.open(f"./img/deck/{suits[deck[i].suit]}/card_{deck[i].value}.png")
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
        self.bid = 0
        self.opp = State.No
        self.opp_bid = 0
        self.pot = 0

    def set_name(self, name):
        self.name = name

    def set_cards(self, data):
        self.hand = [Card(to_suits[data[0]["suit"]], data[0]["value"]), Card(to_suits[data[1]["suit"]], data[1]["value"])]

    def set_community_cards(self, data):
        cards = []
        for i in data:
            cards.append(Card(to_suits[i["suit"]], int(i["value"])))
        print(cards)
        self.deck = cards

    def end_game(self, n):
        if n["winner"] == self.name:
            self.balance += self.pot
            self.balance_label.setText(f"Balance: {self.balance}")

        self.deck = []
        self.hand = []
        self.opp = State.No
        self.bid = 0
        self.pot = 0
        self.opp_bid = 0
        self.pot_label.setText("Pot: 0")
        self.bid_label.setText(f"Your bid: {self.bid}")
        self.opp_bid_label.setText(f"Opponent bid: {self.opp_bid}")
        self.disable_buttons()

    def on_ready_read(self):
        msg = self.sender().readAll()
        print(string_from_byte(msg))
        for f in string_from_byte(msg).split("/n"):
            if f == "":
                continue
            coms = json.loads(f.strip())
            print(coms)
            for data in coms:
                if data["command"] == "set_name":
                    self.set_name(data["name"])
                    if self.name == "player_2":
                        self.disable_buttons()
                    else:
                        self.enable_buttons()
                elif data["command"] == "set_cards":
                    self.set_cards(data["cards"])
                    print(coms)
                elif data["command"] == "set_balance":
                    self.balance = int(data["value"])
                    self.balance_label.setText(f"Balance: {data['value']}")
                    self.raise_slider.setMaximum(self.balance)
                elif data["command"] == "set_community":
                    self.set_community_cards(data["cards"])
                elif data["command"] == "result":
                    if data["winner"] == "player_-1":
                        continue
                    self.end_game(data)
                elif data["command"] == "set_opp":
                    self.enable_buttons()
                    if data["state"] == "Call":
                        self.opp = State.Call
                        self.opp_move_label.setText("Opponent move: Call")
                        self.pot += self.bid - self.opp_bid
                        self.opp_bid = self.bid
                        self.pot_label.setText(f"Pot: {self.pot}")
                        self.opp_bid_label.setText(f"Opponent bid: {self.opp_bid}")
                    elif data["state"] == "Check":
                        self.opp_move_label.setText("Opponent move: Check")
                        self.opp = State.Check
                    elif data["state"] == "Pass":
                        # win condition
                        self.opp_move_label.setText("Opponent move: Pass")
                        self.opp = State.Pass
                    elif data["state"] == "Raise":
                        self.opp = State.Raise
                        self.opp_move_label.setText("Opponent move: Raise")
                        self.opp_bid += int(data["value"])
                        self.pot += int(data["value"])
                        self.pot_label.setText(f"Pot: {self.pot}")
                        self.check_button.setDisabled(True)
                        self.opp_bid_label.setText(f"Opponent bid: {self.opp_bid}")
                        if self.opp_bid - self.bid > self.balance:
                            self.raise_button.setDisabled(True)
                        else:
                            self.raise_slider.setMinimum(self.opp_bid - self.bid if self.opp_bid - self.bid > 0 else 0)
                            self.raise_slider.setMaximum(self.balance)

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
        msg["command"] = "Raise"
        msg["value"] = self.slider_value
        self.write(json.dumps([msg]))
        print(f"raise {self.slider_value} clicked")
        self.pot += self.slider_value
        self.balance -= self.slider_value
        self.balance_label.setText(f"Balance: {self.balance}")
        self.pot_label.setText(f"Pot: {self.pot}")
        self.bid += self.slider_value
        self.raise_slider.setMinimum(self.opp_bid - self.bid if self.opp_bid - self.bid > 0 else 0)
        self.raise_slider.setMaximum(self.balance)
        self.bid_label.setText(f"Your bid: {self.bid}")
        self.disable_buttons()

    @QtCore.pyqtSlot()
    def on_call_button_clicked(self):
        msg = {}
        msg["name"] = self.name
        msg["command"] = "Call"
        self.write(json.dumps([msg]))
        print("call clicked")
        if self.opp_bid - self.bid < self.balance:
            self.balance -= self.opp_bid - self.bid
            self.pot += self.opp_bid - self.bid
            self.bid = self.opp_bid
        else:
            self.balance = 0
            self.pot += self.balance
            self.bid += self.balance
        self.balance_label.setText(f"Balance: {self.balance}")
        self.pot_label.setText(f"Pot: {self.pot}")
        self.bid_label.setText(f"Your bid: {self.bid}")
        self.raise_slider.setMinimum(self.opp_bid - self.bid if self.opp_bid - self.bid > 0 else 0)
        self.raise_slider.setMaximum(self.balance)
        self.disable_buttons()

    def update_background(self):
        print("hand:", self.hand, "\n deck:", self.deck)
        make_table(self.hand, self.deck)
        self.table_pixmap.setPixmap(QPixmap.fromImage(QImage("./img/current_table.png")))

    def write(self, text):
        self.socket.write(str.encode(text + "/n"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PokerApp()
    ex.show()
    sys.exit(app.exec())