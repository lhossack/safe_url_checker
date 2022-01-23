import os
import dbm.dumb as dbm
import shutil

def mkTempDB(test_object) -> None:
    test_object.initial_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    os.makedirs("tmp", exist_ok=True)
    with dbm.open("tmp/tmp", 'c', 0o666) as db:
        db[b"www.evil.com"] = b"Contains malware"
        db[b"www.example.com/index.html"] = b"Contains malware"
        db[b"www.evil.com/index.html?q=download+ram"] = b"Contains malware"
    del db

def rmTempDB(test_object) -> None:
    shutil.rmtree("tmp")
    os.chdir(test_object.initial_dir)
