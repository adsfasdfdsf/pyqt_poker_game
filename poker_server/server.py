from PyQt6.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from PyQt6.QtCore import QObject


from poker_table import PokerTable


class Session(QObject):
    def set_socket(self, socket):
        self.socket = socket
        print(
            "Client Connected from IP %s" % self.socket.peerAddress().toString()
        )


class Server(QObject):
    def __init__(self):
        super().__init__()
        self.port = 7011
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
                self.client1.socket.connected.connect(self.on_connected)
            else:
                self.client2 = Session(self)
                self.client2.set_socket(self.server.nextPendingConnection())
                self.client2.socket.connected.connect(self.on_connected)
                self.client2.socket.disconnected.connect(self.on_connected)
                self.client2.socket.readyRead.connect(self.on_connected)



    def on_connected(self):
        print("client connected")

    def on_ready_read(self):
        print("new message")

    def on_disconnected(self):
        print("client disconnected")

    def start_server(self):
        if self.server.listen(
            QHostAddress.Any, self.port
        ):
            print(
                "Server is listening on port: {}".format(
                    self.port
                )
            )
        else:
            print("Server couldn't wake up")

