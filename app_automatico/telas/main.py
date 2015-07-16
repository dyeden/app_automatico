# -*- coding: utf-8 -*-

import app_automatico
import sys
from layout import *
from PyQt4 import QtGui
from bridge import resultadoValidacao

class validacao(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_carValidacao()
        self.ui.setupUi(self)

    def recebeCar(self):
        self.e = self.ui.municipio_id.text()
        return self.e

    def validaCar(self):
        self.v = self.recebeCar()
        resValid = resultadoValidacao(self)
        resValid.show()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    meuApp = validacao()
    meuApp.show()
    sys.exit(app.exec_())