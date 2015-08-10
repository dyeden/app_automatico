# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'appautomaticodlg.ui'
#
# Created: Sat Jul 25 17:48:22 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_AppAutomaticoDlg(object):
    def setupUi(self, AppAutomaticoDlg):
        AppAutomaticoDlg.setObjectName(_fromUtf8("AppAutomaticoDlg"))
        AppAutomaticoDlg.resize(609, 325)
        self.horizontalLayout = QtGui.QHBoxLayout(AppAutomaticoDlg)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(AppAutomaticoDlg)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.maButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.maButton.setObjectName(_fromUtf8("maButton"))
        self.gridLayout.addWidget(self.maButton, 0, 2, 1, 1)
        self.label = QtGui.QLabel(AppAutomaticoDlg)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.dreButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.dreButton.setObjectName(_fromUtf8("dreButton"))
        self.gridLayout.addWidget(self.dreButton, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(AppAutomaticoDlg)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.ptButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.ptButton.setObjectName(_fromUtf8("ptButton"))
        self.gridLayout.addWidget(self.ptButton, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(AppAutomaticoDlg)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.aprtButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.aprtButton.setObjectName(_fromUtf8("aprtButton"))
        self.gridLayout.addWidget(self.aprtButton, 3, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.saiButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.saiButton.setObjectName(_fromUtf8("saiButton"))
        self.gridLayout.addWidget(self.saiButton, 4, 2, 1, 1)
        self.label_5 = QtGui.QLabel(AppAutomaticoDlg)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.line = QtGui.QFrame(AppAutomaticoDlg)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.closeButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.gridLayout_2.addWidget(self.closeButton, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 1, 0, 1, 1)
        self.iniButton = QtGui.QPushButton(AppAutomaticoDlg)
        self.iniButton.setObjectName(_fromUtf8("iniButton"))
        self.gridLayout_2.addWidget(self.iniButton, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.label_3.setBuddy(self.maButton)
        self.label.setBuddy(self.dreButton)
        self.label_2.setBuddy(self.ptButton)
        self.label_4.setBuddy(self.aprtButton)

        self.retranslateUi(AppAutomaticoDlg)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), AppAutomaticoDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(AppAutomaticoDlg)

    def retranslateUi(self, AppAutomaticoDlg):
        AppAutomaticoDlg.setWindowTitle(_translate("AppAutomaticoDlg", "App Automatico", None))
        self.label_3.setText(_translate("AppAutomaticoDlg", "Poligonos de Massa d Agua", None))
        self.maButton.setText(_translate("AppAutomaticoDlg", "Adicionar", None))
        self.label.setText(_translate("AppAutomaticoDlg", "Linhas de Drenagem", None))
        self.dreButton.setText(_translate("AppAutomaticoDlg", "Adiconar", None))
        self.label_2.setText(_translate("AppAutomaticoDlg", "Pontos de Nascentes", None))
        self.ptButton.setText(_translate("AppAutomaticoDlg", "Adicionar", None))
        self.label_4.setText(_translate("AppAutomaticoDlg", "Limite da Propriedade", None))
        self.aprtButton.setText(_translate("AppAutomaticoDlg", "Adicionar", None))
        self.saiButton.setText(_translate("AppAutomaticoDlg", "Saída", None))
        self.label_5.setText(_translate("AppAutomaticoDlg", "Local de saída de dados", None))
        self.closeButton.setText(_translate("AppAutomaticoDlg", "Fechar", None))
        self.iniButton.setText(_translate("AppAutomaticoDlg", "Iniciar Processo", None))

