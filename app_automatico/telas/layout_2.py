# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test_2.ui'
#
# Created: Wed Apr 15 21:43:00 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_resultadoValidacao(object):
    def setupUi(self, resultadoValidacao):
        resultadoValidacao.setObjectName(_fromUtf8("resultadoValidacao"))
        resultadoValidacao.resize(440, 292)
        self.widget = QtGui.QWidget(resultadoValidacao)
        self.widget.setGeometry(QtCore.QRect(0, 0, 431, 291))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.groupBox = QtGui.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 431, 241))
        self.groupBox.setStyleSheet(_fromUtf8("background-color: white; font-weight: bold; color: rgb(1, 101, 47);"))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(self.groupBox)
        self.tabWidget.setStyleSheet(_fromUtf8("background-color:none;"))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayout = QtGui.QFormLayout(self.tab)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setStyleSheet(_fromUtf8("color: black;"))
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(20, 17, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setStyleSheet(_fromUtf8("color: black;"))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(20, 17, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setStyleSheet(_fromUtf8("color: black;"))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_2.addWidget(self.label_3)
        self.formLayout.setLayout(0, QtGui.QFormLayout.LabelRole, self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setStyleSheet(_fromUtf8("color: black;"))
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        spacerItem2 = QtGui.QSpacerItem(20, 17, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setStyleSheet(_fromUtf8("color: black;"))
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        spacerItem3 = QtGui.QSpacerItem(20, 17, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.label_6 = QtGui.QLabel(self.tab)
        self.label_6.setStyleSheet(_fromUtf8("color: black;"))
        self.label_6.setText(_fromUtf8(""))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.verticalLayout)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(resultadoValidacao)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.label_4, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), resultadoValidacao.nomeFazenda)
        QtCore.QObject.connect(self.label_5, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), resultadoValidacao.areaCar)
        QtCore.QObject.connect(self.label_6, QtCore.SIGNAL(_fromUtf8("customContextMenuRequested(QPoint)")), resultadoValidacao.numeroCar)
        QtCore.QMetaObject.connectSlotsByName(resultadoValidacao)

    def retranslateUi(self, resultadoValidacao):
        resultadoValidacao.setWindowTitle(_translate("resultadoValidacao", "Resultado", None))
        self.label.setText(_translate("resultadoValidacao", "Nome:", None))
        self.label_2.setText(_translate("resultadoValidacao", "Área:", None))
        self.label_3.setText(_translate("resultadoValidacao", "No CAR:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("resultadoValidacao", "Dados Gerais", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("resultadoValidacao", "Sobreposição", None))


        #gamb temporaria - pensar numa forma de atualizar os valores dinamicamente e no main()
        self.label_4.setText("Fazenda Tracajás")
        self.label_5.setText("33517020")
        self.label_6.setText("99753")