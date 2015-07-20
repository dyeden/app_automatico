from PyQt4.QtCore import *
from PyQt4.QtGui import *
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
        # self.updateUi()
    @pyqtSignature("")
    def on_ptButton_clicked(self):
        print "working"
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = AppAutomaticoDlg()
    form.show()
    app.exec_()