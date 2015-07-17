# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created: Wed Apr 15 17:56:47 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from main import *
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

class Ui_carValidacao(object):
    def setupUi(self, carValidacao):
        carValidacao.setObjectName(_fromUtf8("carValidacao"))
        carValidacao.resize(313, 168)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../../Downloads/logoSIGAM_VAZADA_simplificada.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        carValidacao.setWindowIcon(icon)
        self.groupBox = QtGui.QGroupBox(carValidacao)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 321, 171))
        self.groupBox.setStyleSheet(_fromUtf8("background-color:rgb(1, 101, 47);"))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 30, 181, 21))
        self.label.setStyleSheet(_fromUtf8("color: white;\n"
"font-weight: bold"))
        self.label.setObjectName(_fromUtf8("label"))
        self.municipio_id = QtGui.QLineEdit(self.groupBox)
        self.municipio_id.setGeometry(QtCore.QRect(10, 60, 291, 31))
        self.municipio_id.setStyleSheet(_fromUtf8("background-color: white\n"
""))
        self.municipio_id.setObjectName(_fromUtf8("municipio_id"))
        self.validar_municipio = QtGui.QPushButton(self.groupBox)
        self.validar_municipio.setGeometry(QtCore.QRect(200, 110, 98, 27))
        self.validar_municipio.setStyleSheet(_fromUtf8("background-color: white;\n"
"color: rgb(1, 101, 47);\n"
"font-weight: bold;\n"
"border-radius: 3px;"))
        self.validar_municipio.setObjectName(_fromUtf8("validar_municipio"))

        self.retranslateUi(carValidacao)
        QtCore.QObject.connect(self.validar_municipio, QtCore.SIGNAL(_fromUtf8("clicked()")), carValidacao.validaCar)
        QtCore.QObject.connect(self.validar_municipio, QtCore.SIGNAL(_fromUtf8("clicked()")), carValidacao.hide)
        QtCore.QObject.connect(self.municipio_id, QtCore.SIGNAL(_fromUtf8("returnPressed()")), carValidacao.recebeCar)

        QtCore.QMetaObject.connectSlotsByName(carValidacao)

    def retranslateUi(self, carValidacao):
        carValidacao.setWindowTitle(_translate("carValidacao", "CAR", None))
        self.label.setText(_translate("carValidacao", "ID do munícipio:", None))
        self.validar_municipio.setText(_translate("carValidacao", "VALIDAR", None))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    meuApp = validacao()
    meuApp.show()
    sys.exit(app.exec_())