import collections
import os.path
from datetime import datetime

sScannerObject = collections.namedtuple("sScannerObject", "objName objPathId objId objIsDir objSize objTimestamp "
                                                          "objOtherAttributes")

# not in use as of today
# sScannerDirDBObject = collections.namedtuple("sScannerDirDBObject", "objName objPathId objId")

class cFilesystemScanner:
    def __init__(self):
        self.m_ObjectList = []
        self.m_DirectoryList = {}
        self.m_SearchDirectoryName = None
        self.m_isDebugMode = False
        self.m_DirSequence = 0
        self.m_FileSequence = 0

    def setSearchDirectoryName(self, a_DirName):
        self.m_SearchDirectoryName = a_DirName

    def setDebugMode(self, a_Mode):
        if a_Mode == "Y":
            self.m_isDebugMode = True
        else:
            self.m_isDebugMode = False

    def scanDirectory(self):
        if self.m_SearchDirectoryName is None:
            self.m_SearchDirectoryName = '.'
        self.m_DirectoryList[self.m_SearchDirectoryName] = self.m_DirSequence
        for dirpath, dirnames, files in os.walk(self.m_SearchDirectoryName):
            for l_dirName in dirnames:
                self.m_DirSequence += 1
                self.m_DirectoryList[os.path.join(dirpath, l_dirName)] = self.m_DirSequence
                self.m_ObjectList.append(sScannerObject(l_dirName, self.m_DirectoryList[dirpath], self.m_DirSequence,
                                                        "Y", '0', None, None))

            for l_fileName in files:
                l_fileStat = os.stat(os.path.join(dirpath, l_fileName))
                self.m_FileSequence += 1
                self.m_ObjectList.append(sScannerObject(l_fileName, self.m_DirectoryList[dirpath], self.m_FileSequence,
                                                        "N", l_fileStat.st_size,
                                                        datetime.strftime(datetime.fromtimestamp(l_fileStat.st_ctime),
                                                                          "%Y/%d/%m, %H:%M:%S.%f"), None))
        if self.m_isDebugMode:
            print("scanDirectory  :: ", self.m_ObjectList)

    def getDirectoryList(self):
        return self.m_DirectoryList

    def getFilesList(self):
        return self.m_ObjectList