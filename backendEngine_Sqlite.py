import sqlite3
from datetime import datetime
from definitions import sScannerObject

class sqliteDBImporter:
    def __init__(self, a_SQLiteFileName :str):
        self.m_DbPath = a_SQLiteFileName
        self.m_DbConnection = None
        self.m_ImportId = -1
        self.m_DateTime = datetime.now()

    def __del__(self):
        if self.m_DbConnection is not None:
            self.m_DbConnection.close()
            self.m_DbConnection = None

    def sqliteDBConnect(self):
        self.m_DbConnection = sqlite3.connect(self.m_DbPath)
        if self.m_DbConnection is None:
            print("Sqlite connection failed!")
            return False
        return True

    def getNewExportId(self):
        l_queryResult = self.m_DbConnection.cursor()
        l_sqlStatement = "select coalesce(max(objImportId), 1) from discCleaner_ScannerObject"
        l_queryResult.execute(l_sqlStatement)
        return l_queryResult.fetchone()[0]

    def insertScannerObjects(self, a_ScannersObjectsList :list[sScannerObject], a_ImportId :int):
        l_queryCursor = self.m_DbConnection.cursor()
        l_insertNewImport_Query = """INSERT INTO discCleaner_ScannerObject (objName, objPathId, objId, objIsDir, 
                                     objSize, objTimestamp, objOtherAttributes, objImportId) VALUES (?,?,?,?,?,?,?,?)"""
        for tmpObject in a_ScannersObjectsList:
            l_queryCursor.execute(l_insertNewImport_Query, (tmpObject.objName, tmpObject.objPathId, tmpObject.objId,
                                  tmpObject.objIsDir, tmpObject.objSize, tmpObject.objTimestamp, None, a_ImportId,)
                                  )
        l_queryCursor.close()
        self.m_DbConnection.commit()


class sqliteItemExplorer:
    def __init__(self, a_SQLiteFileName :str):
        self.m_DbPath = a_SQLiteFileName
        self.m_DbConnection = None

    def __del__(self):
        if self.m_DbConnection is not None:
            self.m_DbConnection.close()
            self.m_DbConnection = None

    def sqliteDBConnect(self):
        self.m_DbConnection = sqlite3.connect(self.m_DbPath)
        if self.m_DbConnection is None:
            print("Sqlite connection failed!")
            return False
        return True

    def getDuplicatedFilesCandidates(self):
        l_getItemsQuery = """select objName, objSize, count(*) from discCleaner_ScannerObject where objIsDir = 'N' 
                             group by objName, objSize having count(*) > 1"""
        l_sqlCursor = self.m_DbConnection.cursor()
        l_sqlCursor.execute(l_getItemsQuery)
        return l_sqlCursor.fetchall()

    def getDirectoriesList(self):
        l_getItemsQuery = "select objName, objPathId, objId from discCleaner_ScannerObject where objIsDir = 'Y' "
        l_sqlCursor = self.m_DbConnection.cursor()
        l_sqlCursor.execute(l_getItemsQuery)
        return l_sqlCursor.fetchall()

