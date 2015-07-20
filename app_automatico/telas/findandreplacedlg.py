import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# try:
#     import ui_findandreplacedlg
# except:
#     from app_automatico import ui_findandreplacedlg
from app_automatico.telas import ui_findandreplacedlg
class FindAndReplaceDlg(QDialog, ui_findandreplacedlg.Ui_FindAndReplaceDlg):
    def __init__(self, text, parent=None):
        super(FindAndReplaceDlg, self).__init__(parent)
        self.__text = unicode(text)
        self.__index = 0
        self.setupUi(self)
        self.updateUi()

    @pyqtSignature("QString")
    def on_findLineEdit_textEdited(self, text):
        self.__index = 0
        self.updateUi()

    def updateUi(self):
        enable = not self.findLineEdit.text().isEmpty()
        self.findButton.setEnabled(enable)
        self.replaceButton.setEnabled(enable)
        self.replaceAllButton.setEnabled(enable)

    def text(self):
        return self.__text

    @pyqtSignature("")
    def on_findButton_clicked(self):
        regex = self.makeRegex()
        match = regex.search(self.__text, self.__index)
        if match is not None:
            self.__index = match.end()
            self.emit(SIGNAL("found"), match.start())
        else:
            self.emit(SIGNAL("notfound"))

    def makeRegex(self):
        findText = unicode(self.findLineEdit.text())
        if unicode(self.syntaxComboBox.currentText()) == "Literal":
            findText = re.escape(findText)
        flags = re.MULTILINE|re.DOTALL|re.UNICODE
        if not self.caseCheckBox.isChecked():
            flags |= re.IGNORECASE
        if self.wholeCheckBox.isChecked():
            findText = r"\b%s\b" % findText
        return re.compile(findText, flags)

    @pyqtSignature("")
    def on_replaceButton_clicked(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Open File')
        dialog.setNameFilter('Images (*.png *.xpm *.jpg)')
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            filename = dialog.selectedFiles()[0]
        print filename
        print dialog.selectedFiles()
        regex = self.makeRegex()
        self.__text = regex.sub(unicode(self.replaceLineEdit.text()),
        self.__text, 1)

    @pyqtSignature("")
    def on_replaceAllButton_clicked(self):
        regex = self.makeRegex()
        self.__text = regex.sub(unicode(self.replaceLineEdit.text()),
        self.__text)

if __name__ == "__main__":
    import sys
    text = """There are signs of unease about the tone of these laws
    ...
    Quoted from Henry Porter, The Observer, December 31, 2006."""
    def found(where):
        print "Found at %d" % where
    def nomore():
        print "No more found"
    app = QApplication(sys.argv)
    form = FindAndReplaceDlg(text)
    form.connect(form, SIGNAL("found"), found)
    form.connect(form, SIGNAL("notfound"), nomore)
    form.show()
    app.exec_()
    print form.text()