from PyQt5.uic import loadUi
from PyQt5 import  QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidgetItem
from reading_data import FilesReader
from db_connection import CAO_MEASURES

class DataFileDialog(QDialog):
    def __init__(self,signalList,fileNameL):
        self.listCheckBox =signalList
        self.files=fileNameL
        super(DataFileDialog, self).__init__()
        loadUi("/Users/smain/Documents/TX/ui_stress-master/designer/secondW.ui", self)

        self.progressBar.setRange(0,100)
        for i, v in enumerate(signalList):
            item = QListWidgetItem()
            item.setText(v)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if "TimestampSync" in v or "stamp" in v:
                item.setFlags(QtCore.Qt.NoItemFlags)
                item.setCheckState(QtCore.Qt.Checked)
                #item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable )
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.listSignals.addItem(item)

        dividedFileNamePath = self.files[0].split("/")
        onlyNameFile = dividedFileNamePath[len(dividedFileNamePath) - 1]
        fileNameDivided = onlyNameFile.split("_")
        id, sessionId, instrumentName = fileNameDivided[0], fileNameDivided[1], fileNameDivided[2]
        self.idFile =id
        self.sessionId = sessionId
        self.instrument = instrumentName
        self.sessionFile_edtl.setText(sessionId)
        self.idFile_edtl.setText(id)

        self.btn_save_data_db.clicked.connect(self.saveDataDb)
        self.btn_check_all_var.clicked.connect(self.checkAllOptionsVar)

    def checkAllOptionsVar(self):
        for numb in range(self.listSignals.count()):
            item = self.listSignals.item(numb)
            if not item.checkState():
                item.setCheckState(QtCore.Qt.Checked)


    def saveDataDb(self):
        #disable btn while data is saved
        self.btn_save_data_db.setEnabled(False)

        listSignalsText = []
        for numb in range(self.listSignals.count()):
            item = self.listSignals.item(numb)
            if item.checkState():
                listSignalsText.append(item.text())
        fileReader = FilesReader()
        dataFormatted = fileReader.readDataFiles(self.files,listSignalsText)
        caoMeasures = CAO_MEASURES()
        caoMeasures.saveVariablesFile(listSignalsText,self.idFile,self.sessionId,self.instrument )
        caoMeasures.saveDataMeasures(dataFormatted)

        #fill progressBar , so we notified that all the files have been saved
        for i in range(100):
            self.progressBar.setValue(i+1)


