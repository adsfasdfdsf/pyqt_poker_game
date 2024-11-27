from PyQt6.QtWidgets import QWidget, QPushButton, QLabel


class Res(QWidget):
    def __init__(self, winner):
        super().__init__()
        self.winner = winner
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        if self.winner:
            self.setWindowTitle('Win!')
        else:
            self.setWindowTitle("Lose!")

        self.next_button = QPushButton(self)
        self.next_button.move(20, 60)
        self.next_button.setText("next game")
        self.next_button.clicked.connect(self.close)

        self.leave_button = QPushButton(self)
        self.leave_button.move(120, 60)
        self.leave_button.setText("Leave game")
        self.leave_button.clicked.connect(self.close)

        self.label = QLabel(self)
        self.label.setText("Next game will start automatically")
        self.label.move(20, 30)
