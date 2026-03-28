import collections

sScannerObject = collections.namedtuple("sScannerObject", "objName objPathId objId objIsDir objSize objTimestamp "
                                                          "objOtherAttributes")

sScannerDirDBObject = collections.namedtuple("sScannerDirDBObject", "objName objPathId objId")