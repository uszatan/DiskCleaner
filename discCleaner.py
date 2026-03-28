
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

def directoryToList(a_InputDir):
    dirAsList = a_InputDir.strip("/").split("/")
    dirAsList.reverse()
    return dirAsList

test = cDirectoryUtils()
test.setBackendDatabaseName("/Users/piotrbelniak/Google Drive/Mój dysk/dbDiskCleaner.db")
test.getDirectoryList()
test.directoryListToDict()
print(test.getDirectoryPath(999))
print(test.getDirectoryPath(999).strip("/").split("/"))
print( directoryToList( test.getDirectoryPath(9099)))
#print(test.directoryList)
#print(len(test.directoryList))
