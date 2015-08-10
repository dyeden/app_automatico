from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app_automatico import app_automatico
try:
    from app_automatico.telas import ui_appautomaticodlg
except:
    import ui_appautomaticodlg

class AppAutomaticoDlg(QDialog, ui_appautomaticodlg.Ui_AppAutomaticoDlg):
    def __init__(self, id_mun = None, parent = None):
        super(AppAutomaticoDlg, self).__init__(parent)
        self.__id_mun = id_mun
        self.__index = 0
        self.setupUi(self)
        self.__maPath = None
        self.__drePath = None
        self.__ptPath = None
        self.__aprtPath = None
        self.__saiPath = None
        # self.updateUi()


    @pyqtSignature("")
    def on_maButton_clicked(self):
        print "massa dagua"
        dialog = QFileDialog(self)
        dialog.setNameFilter('Shapefile (*.shp)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.__maPath =  str(dialog.selectedFiles()[0])



    @pyqtSignature("")
    def on_dreButton_clicked(self):
        print "drenagem"
        dialog = QFileDialog(self)
        dialog.setNameFilter('Shapefile (*.shp)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.__drePath = dialog.selectedFiles()[0]

    @pyqtSignature("")
    def on_ptButton_clicked(self):
        print "ponto de drenagem"
        dialog = QFileDialog(self)
        dialog.setNameFilter('Shapefile (*.shp)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.__ptPath = dialog.selectedFiles()[0]

    @pyqtSignature("")
    def on_aprtButton_clicked(self):
        print "aprt"
        dialog = QFileDialog(self)
        dialog.setNameFilter('Shapefile (*.shp)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.__aprtPath = dialog.selectedFiles()[0]

    @pyqtSignature("")
    def on_saiButton_clicked(self):
        dialog = QFileDialog(self)
        self.__saiPath = str(dialog.getExistingDirectory())


    @pyqtSignature("")
    def on_iniButton_clicked(self):
        print "iniciar processo"
        print self.__maPath
        print self.__drePath
        print self.__ptPath
        print self.__aprtPath
        print self.__saiPath
        app_processo = app_automatico.DefinirApp(
            self.__maPath, self.__drePath, self.__ptPath, self.__aprtPath, self.__saiPath
        )
        app_processo.main()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = AppAutomaticoDlg()
    form.show()
    app.exec_()