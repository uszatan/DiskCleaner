
from filesystemScan import cFilesystemScanner
from backendEngine_Sqlite import sqliteDBImporter
from backendEngine_Sqlite import sqliteItemExplorer
from directoryUtils import cDirectoryUtils

'''
tmpObject = cFilesystemScanner()
tmpObject.setDebugMode("Y")
tmpObject.setSearchDirectoryName("/home/piotrek/Dokumenty/Python/")
tmpObject.scanDirectory()
tmpObject.getScannedItems()
'''

# dbConn = sqliteDBImporter("/home/piotrek/Pobrane/dbDiskCleaner.db")
# dbConn.sqliteDBConnect()
# print(dbConn.getNewExportId())

# getData = sqliteItemExplorer("/home/piotrek/Pobrane/dbDiskCleaner.db")
# getData.sqliteDBConnect()
# print(getData.getDirectoriesList())

test = cDirectoryUtils()
test.setBackendDatabaseName("/home/piotrek/Pobrane/dbDiskCleaner.db")
test.getDirectoryList()
test.directoryListToDict()
print(test.getDirectoryPath(993))
#print(test.directoryList)
#print(len(test.directoryList))
