
from scipy.io import loadmat 
import pandas as pd
from tools_signals import ManagerTools
from scipy import signal as signalP
class FilesReader():
    def __init__(self):
        
        self.dataToDb_ = []

    def getDataToDb(self):
        return self.dataToDb_

    def readDataFiles(self,listNameFiles,listSignals):
        """
        Utilisee pour recuperer les valeurs de la liste des  signaux listSignals
        a partir du nom de fichier  listNameFiles. D'abord on fait la distinction 
        entre les fichiers .mat et .csv .
        """
        for fileName in listNameFiles:
            dividedFileNamePath=fileName.split("/")
            onlyNameFile = dividedFileNamePath[len(dividedFileNamePath)-1]
            fileNameDivided = onlyNameFile.split("_")
            if(fileNameDivided[len(fileNameDivided)-1] == "PC.mat"):
                self.readDataFileMAT(fileName,listSignals)
            elif(fileNameDivided[len(fileNameDivided)-1] == "PC.csv"):
                self.readDataFileCSV(fileName,listSignals)
        return self.getDataToDb()


    def readDataFileMAT(self,fileName,listSelectedSignals):
        """
        Utilisee pour recuperer les valeurs de la liste des  signaux listSelectedSignals
        a partir du nom de fichier  fileName a partir d'un fichier .mat .
        Une fois les donnees sont lus , on passe a leur sauvegarder dans la BD.
        """
        data = loadmat(fileName)
        dividedFileNamePath = fileName.split("/")
        onlyNameFile = dividedFileNamePath[len(dividedFileNamePath) - 1]
        fileNameDivided = onlyNameFile.split("_")
        print(dividedFileNamePath)
        print(fileNameDivided)
        id, sessionId, instrumentName = fileNameDivided[0], fileNameDivided[1], fileNameDivided[2]

        timeStampDevice = [signal for signal in listSelectedSignals if "TimestampSync" in signal or "stamp" in signal][0]

        timeStamps = data[timeStampDevice].flatten(order="C")
        for signalName in listSelectedSignals:
            if "TimestampSync" not in signalName or "stamp" not in signalName:
                flattenData = data[signalName].flatten(order="C")
                  
                for signalValue, timeStamp in zip(flattenData, timeStamps):
                    self.dataToDb_.append(
                        (id, sessionId, instrumentName, signalName, float(signalValue), float(timeStamp / 1000)))
                

    def readDataFileCSV(self,fileName,listSelectedSignals):
        """
        Utilisee pour recuperer les valeurs de la liste des  signaux listSelectedSignals
        a partir du nom de fichier  fileName a partir d'un fichier .csv .
        Une fois les donnees sont lus , on passe a leur sauvegarder dans la BD.
        """
        content = pd.read_csv(fileName)
        content.dropna()
        dividedFileNamePath = fileName.split("/")
        onlyNameFile = dividedFileNamePath[len(dividedFileNamePath) - 1]
        fileNameDivided = onlyNameFile.split("_")
        id, sessionId, instrumentName = fileNameDivided[0], fileNameDivided[1], fileNameDivided[2]

        timeStampDevice = [signal for signal in listSelectedSignals if "TimestampSync" in signal or "stamp" in signal][0]

        dfTimeStamp = pd.DataFrame(content, columns=[timeStampDevice])
        timeStamps = dfTimeStamp.values.flatten(order="C")
        for signalName in listSelectedSignals:
            if "TimestampSync" not in signalName or "stamp" not in signalName:
                dfVar = pd.DataFrame(content, columns=[signalName])

                sigValues = dfVar.values.flatten(order="C")

                for signalValue, timeStamp in zip(sigValues, timeStamps):
                    self.dataToDb_.append(
                        (id, sessionId, instrumentName, signalName, float(signalValue), float(timeStamp / 1000)))

    def getSingalIListMat(self,fileName):
        data = loadmat(fileName)
        keys = [key for key in data if "__" not in key]
        return keys

    def getSignalListCsv(self,fileName):
        content = pd.read_csv(fileName)
        keys = [key for key in content]
        return keys

    def getSignalListFromFile(self,listNameFiles):
        for fileName in listNameFiles:
            dividedFileNamePath=fileName.split("/")
            onlyNameFile = dividedFileNamePath[len(dividedFileNamePath)-1]
            fileNameDivided = onlyNameFile.split("_")
            if(fileNameDivided[len(fileNameDivided)-1] == "PC.mat"):
                return self.getSingalIListMat(fileName)
            elif(fileNameDivided[len(fileNameDivided)-1] == "PC.csv"):
                return self.getSignalListCsv(fileName)



