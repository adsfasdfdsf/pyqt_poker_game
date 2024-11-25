import sys
from PyQt6.QtNetwork import QTcpServer, QTcpSocket
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication
import json


from poker_table import PokerTable
from card import suits


def string_from_byte(n):
    return str(n.data())[2:-1]


class Session(QObject):
    def set_socket(self, socket):
        self.socket = socket
        print(
            "Client Connected from IP %s" % self.socket.peerAddress().toString()
        )

    def write(self, text):
        self.socket.write(str.encode(text))


class Server(QObject):
    def __init__(self):
        super().__init__()
        self.port = 50051
        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.players = 0
        self.poker_table = PokerTable(1000, 1000)
        self.client1 = None
        self.client2 = None
        self.opened_last = []

    def handle_new_connection(self):
        while self.server.hasPendingConnections() and self.players < 2:
            self.players += 1
            print("Incoming Connection...")
            if self.client1 is None:
                self.client1 = Session(self)
                self.client1.set_socket(self.server.nextPendingConnection())
                self.client1.socket.disconnected.connect(self.on_disconnected)
                self.client1.socket.readyRead.connect(self.on_ready_read)
            else:
                self.client2 = Session(self)
                self.client2.set_socket(self.server.nextPendingConnection())
                self.client2.socket.disconnected.connect(self.on_disconnected)
                self.client2.socket.readyRead.connect(self.on_ready_read)
            if (self.client1 is not None) and (self.client2 is not None):
                self.start_game()



    def start_game(self):
        self.meet_player(1)
        self.meet_player(2)


    def meet_player(self, num):
        if num == 1:
            print("meet 1")
            data = {}
            c1 = {}
            c1["suit"] = suits[self.poker_table.cards1[0].suit]
            c1["value"] = self.poker_table.cards1[0].value
            c2 = {}
            c2["suit"] = suits[self.poker_table.cards1[1].suit]
            c2["value"] = self.poker_table.cards1[1].value
            data["command"] = "set_cards"
            data["cards"] = [c1, c2]

            data2 = {}
            data2["command"] = "set_balance"
            data2["value"] = self.poker_table.balance1

            data3 = {}
            data3["command"] = "set_name"
            data3["name"] = "player_1"

            msg = json.dumps([data3, data, data2])
            print(msg)
            self.client1.write(msg)
        else:
            print("meet 2")
            data = {}
            c1 = {}
            c1["suit"] = suits[self.poker_table.cards2[0].suit]
            c1["value"] = self.poker_table.cards2[0].value
            c2 = {}
            c2["suit"] = suits[self.poker_table.cards2[1].suit]
            c2["value"] = self.poker_table.cards2[1].value

            data["command"] = "set_cards"
            data["cards"] = [c1, c2]

            data2 = {}
            data2["command"] = "set_balance"
            data2["value"] = self.poker_table.balance2

            data3 = {}
            data3["command"] = "set_name"
            data3["name"] = "player_2"

            msg = json.dumps([data3, data, data2])
            print(msg)
            self.client2.write(msg)


    def pass_option(self, msg):
        if msg["name"] == "player_1":
            self.poker_table.first_pass()
        else:
            self.poker_table.second_pass()


    def check_option(self, msg):
        if msg["name"] == "player_1":
            self.poker_table.first_check()
        else:
            self.poker_table.second_check()

    def raise_option(self, msg):
        if msg["name"] == "player_1":
            self.poker_table.first_raise(int(msg["value"]))
        else:
            self.poker_table.second_raise(int(msg["value"]))

    def call_option(self, msg):
        if msg["name"] == "player_1":
            self.poker_table.first_call()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Call"
            print("from 1 to 2")
            self.client2.write(json.dumps([data]))
        else:
            self.poker_table.second_call()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Call"
            print("from 2 to 1")
            self.client1.write(json.dumps([data]))

    def on_ready_read(self):
        msg = self.sender().readAll()
        print(string_from_byte(msg))
        coms = json.loads(string_from_byte(msg))
        print(coms)
        for data in coms:
            if data["command"] == "Pass":
                self.pass_option(data)
            elif data["command"] == "Check":
                self.check_option(data)
            elif data["command"] == "Raise":
                self.raise_option(data)
            elif data["command"] == "Call":
                self.call_option(data)






    def on_disconnected(self):
        print("client disconnected") #TODO free slot

    def start_server(self):
        if self.server.listen(port=self.port):
            print("Server is listening on port: {}".format(self.port))
        else:
            print("Server couldn't wake up")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Server()
    ex.start_server()
    sys.exit(app.exec())