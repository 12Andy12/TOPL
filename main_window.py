import os.path
import sqlite3
import sys
import time
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
import sqlite3


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сюда вставить название")

        self.tableStyle = "QTableWidget{\ngridline-color: #666666}"
        self.treeStyle = "QHeaderView::section {background-color: rgb(50, 50, 50);\ncolor: #b1b1b1;\npadding-left: 4px;\nborder: 1px solid #6c6c6c;\n}\n" \
                         "QHeaderView::section:hover{background-color: rgb(50, 50, 50);\nborder: 2px solid #ca8ad8;\ncolor: #fff;\n}\n" \
                         "QTreeView{show-decoration-selected: 1;\noutline: 0;\n}\n" \
                         "QTreeView::item {\ncolor: #b1b1b1;\n}\n" \
                         "QTreeView::item:hover{background: rgba(80, 120, 242, 100);\nborder-top: 1px solid #002cf2;\nborder-bottom: 1px solid #002cf2;\n}\n" \
                         "QTreeView::item:selected {background: rgb(80, 120, 242)}"
        self.headerStyle = "::section:pressed {background-color: #323232;\nborder: none;}\n::section {background-color: #323232;\nborder: none;}"
        self.btnCloseStyle = ":hover{\nbackground-color: darkred;\n}\n:pressed{\nbackground-color: red;\n}\nQPushButton{border:none}"
        self.btnChangeStyle = ":hover{\nbackground-color: darkorange;\n}\n:pressed{\nbackground-color: orange;\n}\nQPushButton{border:none}"
        self.btnOpenStyle = ':hover{\nbackground-color: darkgreen;\n}\n:pressed{\nbackground-color: green;\n}\nQPushButton{border:none} '
        self.btnFolderStyle = ':hover{\nbackground-color: darkgreen;\n}\n:pressed{\nbackground-color: green;\n}\nQPushButton{border:none;\ntext-align: left;\nfont: 20px;} '

        uic.loadUi('main_window.ui', self)
        self.maxStepCount = 5
        # self.wordSize = 2
        self.alphabet = ["a", "b"]
        self.N = ["S", "C", "D", "A", "B"]
        self.rules = {
            "S": ["CD"],
            "C": ["aCA", "bCB", ""],
            "AD": ["aD"],
            "BD": ["bD"],
            "Aa": ["aA"],
            "Ab": ["bA"],
            "Ba": ["aB"],
            "Bb": ["bB"],
            "D": [""]
        }

        self.result = []
        self.absoluteResult = set()

        self.startData.setText("Дана грамматика G = (Σ, N, P, S), где Σ = {}, N = {S, }")
        self.labelRules.setText("Правила вывода P имеют вид:")
        self.initRulesTable()
        self.initAlphabetTable()
        self.initNTable()

        self.btnGenerate.clicked.connect(self.startGenerate)

        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels([''])
        self.treeWidget.header().hide()
        self.treeWidget.setStyleSheet(self.treeStyle)

        # root = QTreeWidgetItem(self.treeWidget)
        # root.setText(0, "S")
        # child1 = QTreeWidgetItem()
        # child1.setText(0, 'child1')
        # root.addChild(child1)
        # child2 = QTreeWidgetItem(root)
        # child2.setText(0, 'child2')
        # child3 = QTreeWidgetItem(child2)
        # child3.setText(0, 'child3')

        # self.treeWidget.addTopLevelItem(root)

    def startGenerate(self):
        self.println("generating start")
        self.getN()

        if "S" not in self.N:
            QMessageBox.about(self, "Ошибка", "N должен содержать стартовый символ")
            return
        self.getAlphabet()
        if len(self.alphabet) == 0:
            QMessageBox.about(self, "Ошибка", "Алфавит должен содержать символы")
            return
        self.getRules()
        if "S" not in self.rules:
            QMessageBox.about(self, "Ошибка", "Правила P должены содержать стартовый символ")
            return
        if self.stepsCountLineEdit is None:
            QMessageBox.about(self, "Ошибка", "Необходимо указать количество шагов")
            return
        if not self.stepsCountLineEdit.text().isdigit():
            QMessageBox.about(self, "Ошибка", f"количество шагов должно быть числом{self.stepsCountLineEdit.text()}")
            return

        self.maxStepCount = int(self.stepsCountLineEdit.text())

        resultStartData = "Дана грамматика G = (Σ, N, P, S), где Σ = {"

        for i in self.alphabet:
            resultStartData += i + ", "

        resultStartData += "}, N = {"

        for i in self.N:
            resultStartData += i + ", "

        resultStartData += "}"

        self.startData.setText(resultStartData)

        root = QTreeWidgetItem(self.treeWidget)
        root.setText(0, "S")
        self.generate(root)
        self.normaliseResult()

        self.println(f"generating completed: {self.absoluteResult}")

    def generate(self, thisNode, stepCount=0):
        if stepCount >= self.maxStepCount or thisNode.text(0) == "":
            # print(f"answer = {thisWord}")
            return

        for key in self.rules:
            if key not in thisNode.text(0):
                continue

            for val in self.rules[key]:
                # print(f"{stepCount}) {thisNode.text(0)} ({key}: {val})")
                child = QTreeWidgetItem(thisNode)
                child.setText(0, thisNode.text(0).replace(key, val, 1))
                self.result.append(child.text(0))
                self.generate(child, stepCount + 1)

    def getN(self):
        self.println("Get N started")
        self.N = []
        NW = self.nWidget
        for i in range(NW.rowCount() - 1):
            if NW.item(i, 0) is not None:
                self.N.append(NW.item(i, 0).text())
        self.println(f"Get N completed, N = {self.N}")

    def getAlphabet(self):
        self.println("Get alphabet started")
        self.alphabet = []
        alphabet = self.alphabetWidget
        for i in range(alphabet.rowCount() - 1):
            if alphabet.item(i, 0) is not None:
                self.alphabet.append(alphabet.item(i, 0).text())
        self.println(f"Get alphabet completed, alphabet = {self.alphabet}")

    def getRules(self):
        self.println("Get rules started")
        self.rules = {}
        rules = self.rulesWidget
        for i in range(rules.rowCount() - 1):
            if rules.item(i, 0) is None:
                continue

            if rules.item(i, 2) is None:
                rules.setItem(i, 2, QtWidgets.QTableWidgetItem(""))

            if rules.item(i, 0).text() in self.rules:
                val = self.rules[rules.item(i, 0).text()]
                val.append(rules.item(i, 2).text())
                self.rules[rules.item(i, 0).text()] = val
            else:
                self.rules[rules.item(i, 0).text()] = [rules.item(i, 2).text()]

        self.println(f"Get rules completed, rules = {self.rules}")

    def initRulesTable(self):
        self.println("Init rules tabel started")
        rules = self.rulesWidget
        rules.horizontalHeader().setStyleSheet(self.headerStyle)
        rules.setStyleSheet(self.tableStyle)
        rules.verticalHeader().hide()

        rules.setColumnCount(4)

        rules.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        rules.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        rules.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        rules.setColumnWidth(1, 30)
        rules.setColumnWidth(3, 40)

        rules.setHorizontalHeaderLabels(['', '', '', ''])
        rules.setRowCount(rules.rowCount() + 1)
        rules.setSpan(rules.rowCount() - 1, 0, 1, 4)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addRules)
        rules.setCellWidget(rules.rowCount() - 1, 0, btnAdd)
        self.println("Init rules tabel completed")

    def addRules(self):
        self.println("Add row inside rules table started")
        rules = self.rulesWidget
        rules.setSpan(rules.rowCount() - 1, 0, 1, 1)
        rules.setItem(rules.rowCount() - 1, 1, QtWidgets.QTableWidgetItem("->"))
        rules.item(rules.rowCount() - 1, 1).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        rules.setCellWidget(rules.rowCount() - 1, 0, None)
        btnDel = QPushButton()
        btnDel.setIcon(QIcon("iconClose.png"))
        btnDel.setIconSize(QSize(20, 20))
        btnDel.setStyleSheet(self.btnCloseStyle)
        btnDel.clicked.connect(lambda: self.DelCurrentRow(rules))
        rules.setCellWidget(rules.rowCount() - 1, 3, btnDel)

        rules.setRowCount(rules.rowCount() + 1)
        rules.setSpan(rules.rowCount() - 1, 0, 1, 4)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addRules)
        rules.setCellWidget(rules.rowCount() - 1, 0, btnAdd)

        rules.selectionModel().clear()
        self.println("Add row inside rules table completed")

    def initAlphabetTable(self):
        self.println("Init alphabet tabel started")
        alphabet = self.alphabetWidget
        alphabet.horizontalHeader().setStyleSheet(self.headerStyle)
        alphabet.setStyleSheet(self.tableStyle)
        alphabet.verticalHeader().hide()

        alphabet.setColumnCount(2)

        alphabet.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        alphabet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        alphabet.setColumnWidth(1, 40)

        alphabet.setHorizontalHeaderLabels(['', ''])
        alphabet.setRowCount(alphabet.rowCount() + 1)
        alphabet.setSpan(alphabet.rowCount() - 1, 0, 1, 2)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addAlphabet)
        alphabet.setCellWidget(alphabet.rowCount() - 1, 0, btnAdd)
        self.println("Init alphabet tabel completed")

    def addAlphabet(self):
        self.println("Add row inside alphabet table started")
        alphabet = self.alphabetWidget

        alphabet.setSpan(alphabet.rowCount() - 1, 0, 1, 1)
        alphabet.setCellWidget(alphabet.rowCount() - 1, 0, None)

        btnDel = QPushButton()
        btnDel.setIcon(QIcon("iconClose.png"))
        btnDel.setIconSize(QSize(20, 20))
        btnDel.setStyleSheet(self.btnCloseStyle)
        btnDel.clicked.connect(lambda: self.DelCurrentRow(alphabet))
        alphabet.setCellWidget(alphabet.rowCount() - 1, 1, btnDel)

        alphabet.setRowCount(alphabet.rowCount() + 1)
        alphabet.setSpan(alphabet.rowCount() - 1, 0, 1, 2)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addAlphabet)
        alphabet.setCellWidget(alphabet.rowCount() - 1, 0, btnAdd)

        alphabet.selectionModel().clear()
        self.println("Add row inside alphabet table completed")

    def initNTable(self):
        self.println("Init N tabel started")
        N = self.nWidget
        N.horizontalHeader().setStyleSheet(self.headerStyle)
        N.setStyleSheet(self.tableStyle)
        N.verticalHeader().hide()

        N.setColumnCount(2)

        N.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        N.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        N.setColumnWidth(1, 40)

        N.setHorizontalHeaderLabels(['', ''])
        N.setRowCount(N.rowCount() + 1)
        N.setSpan(N.rowCount() - 1, 0, 1, 2)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addN)
        N.setCellWidget(N.rowCount() - 1, 0, btnAdd)
        self.println("Init N tabel completed")

    def addN(self):
        self.println("Add row inside N table started")
        N = self.nWidget

        N.setSpan(N.rowCount() - 1, 0, 1, 1)
        N.setCellWidget(N.rowCount() - 1, 0, None)

        btnDel = QPushButton()
        btnDel.setIcon(QIcon("iconClose.png"))
        btnDel.setIconSize(QSize(20, 20))
        btnDel.setStyleSheet(self.btnCloseStyle)
        btnDel.clicked.connect(lambda: self.DelCurrentRow(N))
        N.setCellWidget(N.rowCount() - 1, 1, btnDel)

        N.setRowCount(N.rowCount() + 1)
        N.setSpan(N.rowCount() - 1, 0, 1, 2)

        btnAdd = QPushButton()
        btnAdd.setText("+")
        # btnAdd.setIcon(QIcon("iconOpen.png"))
        # btnAdd.setIconSize(QSize(20, 20))
        btnAdd.setStyleSheet(self.btnOpenStyle)
        btnAdd.clicked.connect(self.addN)
        N.setCellWidget(N.rowCount() - 1, 0, btnAdd)

        N.selectionModel().clear()
        self.println("Add row inside N table completed")

    def normaliseResult(self):
        for word in self.result:
            is_correct = True
            for key in self.N:
                if key in word:
                    is_correct = False
                    break
            if is_correct:
                self.absoluteResult.add(word)



    def DelCurrentRow(self, table):
        self.println("Deleting row inside table start")
        row = table.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            table.removeRow(row)
            table.selectionModel().clear()
            self.println("Deleting row inside table completed")

    def println(self, text):
        current_datetime = datetime.now()
        self.log.setText(str(current_datetime) + ": " + str(text) + "\n" + self.log.text())
        logFile = open("log.txt.", "a")
        logFile.write(str(current_datetime) + ": " + str(text) + "\n")
        logFile.close()
