import hashlib
import traceback

def getFileMd5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def getBinaryMd5(fdata):
    hash_md5 = hashlib.md5()    
    hash_md5.update(fdata)
    return hash_md5.hexdigest()

def logExceptionWithTraceBack(logger, exception):
    logger.error("%s", exception)
    logger.error("StackTrace Info : %s", ''.join(traceback.format_tb(exception.__traceback__)))

def isAscii(s):
    return all(ord(c) < 128 for c in s)