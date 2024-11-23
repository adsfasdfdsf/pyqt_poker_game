import sys
from PyQt6.QtNetwork import QTcpServer, QTcpSocket
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication
import json


from poker_table import PokerTable
from card import suits


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
                msg = {}
                msg["command"] = "set_name"
                msg["name"] = "player_1"
                self.client1.write(json.dumps(msg))
            else:
                self.client2 = Session(self)
                self.client2.set_socket(self.server.nextPendingConnection())
                self.client2.socket.disconnected.connect(self.on_disconnected)
                self.client2.socket.readyRead.connect(self.on_ready_read)
                msg = {}
                msg["command"] = "set_name"
                msg["name"] = "player_2"
                self.client2.write(json.dumps(msg))
            if (self.client1 is not None) and (self.client2 is not None):
                self.start_game()



    def start_game(self):
        self.meet_player(1)
        self.meet_player(2)


    def meet_player(self, num):
        if num == 1:
            data = {}
            data["command"] = "set_cards"
            c1 = {}
            c1["suit"] = suits[self.poker_table.cards1[0].suit]
            c1["value"] = self.poker_table.cards1[0].value
            c2 = {}
            c2["suit"] = suits[self.poker_table.cards1[1].suit]
            c2["value"] = self.poker_table.cards1[1].value

            data["cards"] = [c1, c2]
            msg = json.dumps(data)
            print(msg)
            self.client1.write(msg)
        else:
            data = {}
            c1 = {}
            c1["suit"] = suits[self.poker_table.cards2[0].suit]
            c1["value"] = self.poker_table.cards2[0].value
            c2 = {}
            c2["suit"] = suits[self.poker_table.cards2[1].suit]
            c2["value"] = self.poker_table.cards2[1].value

            data["cards"] = [c1, c2]
            msg = json.dumps(data)
            print(msg)
            self.client2.write(msg)




    def on_ready_read(self):
        msg = self.sender().readAll()
        data = json.load(msg)
        if data["command"] == "":
            pass #TODO handle commands






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