# Form implementation generated from reading ui file 'poker_client/poker_client_ui.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap, QImage


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(847, 603)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.table_pixmap = QtWidgets.QLabel(parent=self.centralwidget)
        self.table_pixmap.setGeometry(QtCore.QRect(0, 50, 861, 451))
        self.table_pixmap.setScaledContents(True)
        self.table_pixmap.setObjectName("table_pixmap")
        self.pot_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.pot_label.setGeometry(QtCore.QRect(10, 10, 101, 31))
        self.pot_label.setObjectName("pot_label")
        self.raise_slider = QtWidgets.QSlider(parent=self.centralwidget)
        self.raise_slider.setGeometry(QtCore.QRect(330, 560, 160, 22))
        self.raise_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.raise_slider.setObjectName("raise_slider")
        self.check_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.check_button.setGeometry(QtCore.QRect(10, 550, 113, 32))
        self.check_button.setObjectName("check_button")
        self.call_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.call_button.setGeometry(QtCore.QRect(160, 550, 113, 32))
        self.call_button.setObjectName("call_button")
        self.raise_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.raise_button.setGeometry(QtCore.QRect(520, 550, 113, 32))
        self.raise_button.setObjectName("raise_button")
        self.pass_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pass_button.setGeometry(QtCore.QRect(680, 550, 113, 32))
        self.pass_button.setObjectName("pass_button")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(350, 540, 131, 16))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.table_pixmap.setPixmap(QPixmap.fromImage(QImage("./img/poker_table.png")))
        self.table_pixmap.setScaledContents(True)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.table_pixmap.setText(_translate("MainWindow", "TextLabel"))
        self.pot_label.setText(_translate("MainWindow", "TextLabel"))
        self.check_button.setText(_translate("MainWindow", "Check"))
        self.call_button.setText(_translate("MainWindow", "Call"))
        self.raise_button.setText(_translate("MainWindow", "Raise"))
        self.pass_button.setText(_translate("MainWindow", "Pass"))
        self.label.setText(_translate("MainWindow", "Amount to raise:"))
