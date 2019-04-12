from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox,
                             QFormLayout, QGroupBox, QPushButton,
                             QLabel, QLineEdit,
                             QVBoxLayout)
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtWidgets
import sys, requests
refresh_token = ''
access_token = ''


class HomeWindow(QtWidgets.QMainWindow):                                   #Home Window after Login
    def __init__(self, parent=None):
        super(HomeWindow, self).__init__(parent)
        global access_token
        vlayout = QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout1 = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(vlayout)

        lbl = QPushButton('Logout')                                        #Logout widget
        lbl.clicked.connect(self.logout_handler)
        lbl.setMaximumWidth(80)
        hlayout.addWidget(lbl)
        hlayout.setAlignment(Qt.AlignLeft)
        hlayout.setAlignment(Qt.AlignTop)
        vlayout.addLayout(hlayout)

        get_stores_button = QPushButton('Get Stores')                      #Get Stores Widget
        get_stores_button.setMaximumWidth(80)
        get_stores_button.setMaximumHeight(70)
        hlayout1.addWidget(get_stores_button)
        vlayout.addLayout(hlayout1)
        get_stores_button.clicked.connect(self.get_stores_handler)

        self.setCentralWidget(widget)
        self.setGeometry(400, 400, 400, 400)
        self.setWindowTitle('Home')

    @pyqtSlot()
    def logout_handler(self):
        print('Logging Out!')
        global access_token
        headers = {
            'Authorization': 'Bearer '+access_token
        }

        req = requests.post('http://139.59.33.251/logout', data=None, headers=headers)
        access_token = ''
        print(req.status_code)
        if req.status_code == 200:
            QMessageBox.information(self, 'Thanks!', "Logged Out!", QMessageBox.Ok)
            self.close()
        else:
            QMessageBox.information(self, 'Err!', "Error Logging Out", QMessageBox.Ok)
            self.close()

    @pyqtSlot()
    def get_stores_handler(self):
        try:
            self.displaytable = Displaystores()
            self.displaytable.show()
        except Exception as e:
            print(e)


class Displaystores(QtWidgets.QMainWindow):                           #display stores in another window as a table
    def __init__(self, parent=None):
        super(Displaystores, self).__init__(parent)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        req = requests.get('http://139.59.33.251/stores')
        data = req.json()

        table = QtWidgets.QTableWidget()
        table.setRowCount(len(data['stores']))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Store", "Items"])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        headervert = table.verticalHeader()
        headervert.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        row = 0
        for store in data['stores']:
            item = ''
            if len(store['items']) >= 1:
                for ite in store['items']:
                    item += ' | '+ite['name'] + '   $' + str(ite['price'])
            table.setItem(row, 0, QtWidgets.QTableWidgetItem(store['name']))
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(item))
            row += 1

        grid = QtWidgets.QGridLayout()
        grid.addWidget(table)
        layout.addLayout(grid)

        self.setCentralWidget(widget)
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle('Stores-Items')


class Dialog(QDialog):                                                          #login/Register Window
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()
        self.home = None
        self.createFormGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addStretch()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addStretch()
        mainLayout.setContentsMargins(50, 100, 50, 100)
        self.setLayout(mainLayout)

        self.setWindowTitle("Items you Like")

    @pyqtSlot()
    def login_handler(self):
        print('login in')
        un = self.username.text()
        pw = self.password.text()
        data = {
            'username': un,
            'password': pw
        }
        if len(un) == 0 or len(pw) == 0:
            QMessageBox.warning(self, 'Snap!', "Empty Field", QMessageBox.Ok)
        else:
            req = requests.post('http://139.59.33.251/login', data=data)
            print(req.status_code)
            resp = req.json()

            if req.status_code == 401:
                QMessageBox.warning(self, 'Snap!', "No user named "+un, QMessageBox.Ok)
            if req.status_code == 200:
                global refresh_token
                global access_token
                access_token = resp['access_token']
                refresh_token = resp['refresh_token']
                try:
                    self.home = HomeWindow()
                    self.home.show()
                except Exception as e:
                    print(e)

    @pyqtSlot()
    def registration_handler(self):
        print('registering')
        un = self.username.text()
        pw = self.password.text()
        data = {
            'username': un,
            'password': pw
        }
        if len(un) == 0 or len(pw) == 0:
            QMessageBox.warning(self, 'Snap!', "Empty Field", QMessageBox.Ok)
        else:
            req = requests.post('http://139.59.33.251/register', data=data)
            print(req.json(), req.status_code)
            resp = req.json()
            if req.status_code == 400:
                QMessageBox.warning(self, 'Snap!', "Username {} already in use".format(un), QMessageBox.Ok)
            if req.status_code == 201:
                QMessageBox.information(self, 'Success!', "Username {} created. You can Login".format(un), QMessageBox.Ok)

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Welcome to the stores")
        self.formGroupBox.setContentsMargins(50, 50, 50, 50)

        layout = QFormLayout()
        self.username = QLineEdit()
        layout.addRow(QLabel("Username:"), self.username)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow("Password", self.password)

        log = QPushButton('Login')
        reg = QPushButton('Register')
        log.clicked.connect(self.login_handler)
        reg.clicked.connect(self.registration_handler)

        layout.addRow(log, reg)
        self.formGroupBox.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec_())

