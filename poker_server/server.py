from PyQt6.QtNetwork import *
from PyQt6.QtCore import QObject

class Server(QObject):
    def __init__(self):
        super().__init__()
        self.port = 7011
        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.handle_new_connection)


    def handle_new_connection(self):
        while self.server.hasPendingConnections():
            print("Incoming Connection...")
            self.client = Client(self)
            self.client.SetSocket(self.server.nextPendingConnection())

    def start_server(self):
        if self.server.listen(
            QHostAddress.Any, self.port
        ):
            print(
                "Server is listening on port: {}".format(
                    self.TCP_LISTEN_TO_PORT
                )
            )
        else:
            print("Server couldn't wake up")

