# -*- coding: utf-8 -*-

import app_automatico
import sys
from layout import *
from PyQt4 import *
from layout_2 import *

class resultadoValidacao(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_resultadoValidacao()
        self.ui.setupUi(self)


    def nomeFazenda(self):
        self.nome = "Fazenda TESTE Tracajás";

    def areaCar(self):
        self.area = "33517020";


    def numeroCar(self):
        self.numero = "997B3";



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    meuApp = resultadoValidacao()
    meuApp.show()
    sys.exit(app.exec_())
