import mysql
from mysql.connector import connect, Error
from datetime import datetime
import json

f = open('parametre_base_de_donnees.json')
parametre = json.load(f)


class CAO_MEASURES: 
    def __init__(self):
        self.host =parametre["host"]
        self.user =parametre["user"]
        self.pass_ =parametre["password"]
        self.database =parametre["database"]

    def getConnection(self):
        try:
            connection = mysql.connector.connect(host=self.host,
                                                 database=self.database,
                                                 user=self.user,
                                                 password=self.pass_,
                                                 pool_name="mypool",
                                                 pool_size=3
                                                 )
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)
                return connection
        except Error as e:
            print(e)

    def saveDataMeasures(self,data):
        try:
            connection = self.getConnection()
            #connection.query('SET GLOBAL connect_timeout=6000')
            insert_measures="""
            INSERT INTO measures (idPatient,sessionNum,instrumentId,signalType,value,timeMeasure)
            VALUES(%s,%s,%s,%s,%s,%s);
            """
            cursor = connection.cursor()
            cursor.executemany(insert_measures,data)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into measures table")
            cursor.close()
            connection.close()
        except mysql.connector.Error as error:
            print("Failed to insert record into MySQL table {}".format(error))

    def retrieveData(self,idPatient,sessionId,signalType):
        try:
            connection = self.getConnection()
            cursor = connection.cursor()
            query = """SELECT value,timeMeasure FROM measures WHERE idPatient = %s AND sessionNum = %s AND signalType = %s 
            ORDER BY timeMeasure ASC;"""
            cursor.execute(query,(idPatient,sessionId,signalType))
            allData = cursor.fetchall()
            print("Data retrieved")
            xAxeData = []
            yAxeData = []
            print(type(allData))
            for row in allData:
                yAxeData.append(row[0])
                #xAxeData.append(datetime.fromtimestamp(row[1]).time())
                xAxeData.append(row[1])
            print("len x",len(xAxeData))
            print("len y",len(yAxeData))
            return [xAxeData,yAxeData]

        except mysql.connector.Error as e:
            print("Error reading data from MySQL tablw", e)
        finally:
            if connection.is_connected():
                connection.close()
                cursor.close()
                print("MySQL connection is closed")


    def saveVariablesFile(self,listSignals,id,sessionId,instrument):
        try:
            connection = self.getConnection()
            data=[]
            ins = [word for word in instrument if not word.isdigit()]
            instrumentTreaded = "".join(ins)
            for signal in listSignals:
                if "TimestampSync" not in signal or "stamp" not in signal:
                    treadedSingal = signal
                    data.append((id,sessionId,instrumentTreaded,signal,treadedSingal))

            insert_measures="""
            INSERT INTO variables_mesure (idPatient,sessionNum,instrumentId,signalName,signalNameTreaded)
            VALUES(%s,%s,%s,%s,%s);
            """
            cursor = connection.cursor()
            cursor.executemany(insert_measures,data)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into variables_mesure table")
            cursor.close()
            connection.close()
        except mysql.connector.Error as error:
            print("Failed to insert record into MySQL table {}".format(error))


    def retrieveSignalDB(self,idPatient,sessionId,instrument):
        try:
            true_instrument=instrument
            connection = self.getConnection()
            cursor = connection.cursor()
            if instrument=="PPG" :
                instrument="EDA"
            ins = [word for word in instrument if not word.isdigit()]
            instrumentTreaded = "".join(ins)
            query = """SELECT signalName FROM variables_mesure WHERE idPatient = %s AND sessionNum = %s AND instrumentId=%s;"""
            cursor.execute(query,(idPatient,sessionId,instrumentTreaded))
            allData = cursor.fetchall()
            if (true_instrument=="PPG") : 
                allData = [signal for signal in allData if "PPG" in signal[0]]
            if (true_instrument=="EDA") : 
                allData = [signal for signal in allData if "PPG" not in signal[0]]     #-------
            print("Data retrieved variables_mesure")
            return allData

        except mysql.connector.Error as e:
            print("Error reading data from MySQL tablw", e)
        finally:
            if connection.is_connected():
                connection.close()
                cursor.close()
                print("MySQL connection is closed")

    def getVariables(self,signalsDb):
        signals = []
        for signal in signalsDb:
            signals.append(signal[0])
        return signals

    def getVariablesECG(self):
        return ["ECG2_ECG_LL_LA_24BIT_CAL","ECG2_ECG_LL_RA_24BIT_CAL",""]

    def getVariablesEDA(self):
        return ["EDA__1", "EDA__2", "EDA__3"]

    def getVariablesEMG(self):
        return ["EMG__1", "EMG__2", "EMG__3"]

    def saveIdPatient(self,id):
        connection = self.getConnection()
        
    def saveInstrument(self):
        connection = self.getConnection()
        
    def getDataMesure(self,idPatient,sessionId,signalName):
        connection = self.getConnection()
        
