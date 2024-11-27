import json
import sqlite3
import sys
from time import sleep

from PyQt6.QtCore import QObject
from PyQt6.QtNetwork import QTcpServer
from PyQt6.QtWidgets import QApplication

from card import suits
from poker_table import PokerTable


def string_from_byte(n):
    return str(n.data())[2:-1]


class Session(QObject):
    def set_socket(self, socket):
        self.socket = socket
        print(
            "Client Connected from IP %s" % self.socket.peerAddress().toString()
        )

    def write(self, text):
        self.socket.write(str.encode(text + "/n"))


class Server(QObject):
    def __init__(self):
        super().__init__()
        with open("./config", mode="r") as f:
            self.port = int(f.readline().split()[1])
        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.players = 0
        self.poker_table = PokerTable(1000, 1000)
        self.client1 = None
        self.client2 = None
        self.con = sqlite3.connect("balance.sqlite")
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
        prev_winner = self.poker_table.winner
        win = {}
        win["command"] = "result"
        win["winner"] = "player_" + str(prev_winner)

        cur = self.con.cursor()
        res1 = cur.execute(f"""SELECT money FROM Balance
                       WHERE id = ?""", (self.client1.socket.peerAddress().toString(),)).fetchone()

        if not res1:
            cur.execute(f"""INSERT INTO Balance
                                 VALUES (?, ?)""",
                        (self.client1.socket.peerAddress().toString(), self.poker_table.balance1))
        else:
            cur.execute(f"""UPDATE Balance
                           SET money = {self.poker_table.balance1}
                           WHERE id = ?""", (self.client1.socket.peerAddress().toString(),))
        res2 = cur.execute(f"""SELECT money FROM Balance
                               WHERE id = ?""", (self.client2.socket.peerAddress().toString(),)).fetchone()
        if not res2:
            cur.execute(f"""INSERT INTO Balance
                                 VALUES (?, ?)""",
                        (self.client2.socket.peerAddress().toString(), self.poker_table.balance2))
        else:
            cur.execute(f"""UPDATE Balance
                           SET money = {self.poker_table.balance2}
                           WHERE id = ?""", (self.client2.socket.peerAddress().toString(),))
        self.con.commit()
        cur.close()
        self.client1.write(json.dumps([win]))
        self.client2.write(json.dumps([win]))
        self.meet_player(1)
        self.meet_player(2)

    def meet_player(self, num):
        cur = self.con.cursor()
        res1 = cur.execute(f"""SELECT money FROM Balance
                       WHERE id = ?""", (self.client1.socket.peerAddress().toString(),)).fetchone()
        res2 = cur.execute(f"""SELECT money FROM Balance
                       WHERE id = ?""", (self.client2.socket.peerAddress().toString(),)).fetchone()
        cur.close()
        print(res1, "\n", res2)
        self.poker_table = PokerTable(int(res1[0]), int(res2[0]))

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
        com = self.community_cards()
        if msg["name"] == "player_1":
            self.poker_table.first_pass()
        else:
            self.poker_table.second_pass()
        if self.poker_table.winner != -1:
            sleep(2)
            self.start_game()

    def check_option(self, msg):
        com = self.community_cards()
        if msg["name"] == "player_1":
            self.poker_table.first_check()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Check"
            self.client2.write(json.dumps([data, com]))
            self.client1.write(json.dumps([com]))
        else:
            self.poker_table.second_check()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Check"
            self.client1.write(json.dumps([data, com]))
            self.client2.write(json.dumps([com]))
        if self.poker_table.winner != -1:
            sleep(2)
            self.start_game()

    def raise_option(self, msg):
        com = self.community_cards()
        if msg["name"] == "player_1":
            self.poker_table.first_raise(int(msg["value"]))
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Raise"
            data["value"] = msg["value"]
            self.client2.write(json.dumps([data, com]))
            self.client1.write(json.dumps([com]))
        else:
            self.poker_table.second_raise(int(msg["value"]))
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Raise"
            data["value"] = msg["value"]
            self.client1.write(json.dumps([data, com]))
            self.client2.write(json.dumps([com]))

    def call_option(self, msg):
        com = self.community_cards()
        if msg["name"] == "player_1":
            self.poker_table.first_call()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Call"
            self.client2.write(json.dumps([data, com]))
            self.client1.write(json.dumps([com]))
        else:
            self.poker_table.second_call()
            data = {}
            data["command"] = "set_opp"
            data["state"] = "Call"
            self.client1.write(json.dumps([data, com]))
            self.client2.write(json.dumps([com]))
        if self.poker_table.winner != -1:
            sleep(2)
            self.start_game()

    def on_ready_read(self):
        msg = self.sender().readAll()
        print(string_from_byte(msg))
        for f in string_from_byte(msg).split("/n"):
            if f == "":
                continue
            coms = json.loads(f.strip())
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
                elif data["command"] == "Leave":
                    if data["name"] == "player_1":
                        cur = self.con.cursor()
                        cur.execute(f"""UPDATE Balance
                                       SET money = {self.poker_table.balance1}
                                       WHERE id = ?""", (self.client1.socket.peerAddress().toString(),))
                        self.con.commit()
                        self.client1 = None
                        nmsg = {}
                        if self.client2:
                            nmsg["command"] = "result"
                            nmsg["winner"] = "player_2"
                            nmsg2 = {}
                            nmsg2["command"] = "leave"
                            self.client2.write(json.dumps([nmsg, nmsg2]))
                        cur.close()
                    else:
                        cur = self.con.cursor()
                        cur.execute(f"""UPDATE Balance
                                        SET money = {self.poker_table.balance2}
                                        WHERE id = ?""", (self.client2.socket.peerAddress().toString(),))
                        self.con.commit()
                        self.client2 = None
                        nmsg = {}
                        if self.client1:
                            nmsg["command"] = "result"
                            nmsg["winner"] = "player_1"
                            nmsg2 = {}
                            nmsg2["command"] = "leave"
                            self.client1.write(json.dumps([nmsg, nmsg2]))
                        cur.close()
                    return

    def community_cards(self):
        data = {}
        data["command"] = "set_community"
        cards = []
        for i in self.poker_table.open:
            f = {}
            f["suit"] = suits[i.suit]
            f["value"] = i.value
            cards.append(f)
        data["cards"] = cards
        return data

    def on_disconnected(self):
        print("client disconnected")
        self.players -= 1

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
