from backendEngine_Sqlite import sqliteItemExplorer

class cDirectoryUtils:
    def __init__(self):
        self.directoryList = []
        self.directoryDict = {}
        self.sqliteBackendDatabase = None

    def setBackendDatabaseName(self, a_DatabaseNameFile: str):
        """
        set name of database which keeps harvested metadata
        :param a_DatabaseNameFile: ladnie to nazwij
        :return:
        """
        self.sqliteBackendDatabase = a_DatabaseNameFile

    # returns list of folders (directories) from the metadata database
    def getDirectoryList(self):
        itemExplorer = sqliteItemExplorer(self.sqliteBackendDatabase)
        itemExplorer.sqliteDBConnect()
        self.directoryList = itemExplorer.getDirectoriesList()

    def directoryListToDict(self):
        for item in self.directoryList:
            self.directoryDict[item[2]] = item

    def getDirectoryPath(self, a_DirectoryId: int) -> int:
        tmpDirId = a_DirectoryId
        tmpPath = []
        while tmpDirId !=0:
            tmpPath.append(self.directoryDict[tmpDirId][0])
            tmpDirId = self.directoryDict[tmpDirId][1]
        resPath = "/"
        while len(tmpPath) > 0:
            resPath = resPath + tmpPath.pop(len(tmpPath)-1) + "/"
        return resPath

