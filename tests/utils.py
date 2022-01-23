import os
import dbm.dumb as dbm
import shutil


# Lists of urls to populate various databases with
memory_urls = ["example.com/index.html", "www.example.com/index.html"]

dbm_malware_urls = [
    "evil.com",
    "evil.com/path",
    "www.evil.com",
    "www.evil.com/",
    "www.evil.com/index.html?q=download+ram",
]


def mkTempDB(test_object) -> None:
    """Create dbm database at tmp/tmp, populated with utils.malware_urls"""
    test_object.initial_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    os.makedirs("tmp", exist_ok=True)
    with dbm.open("tmp/tmp", "c", 0o666) as db:
        for url in dbm_malware_urls:
            db[url.encode("utf-8")] = b"Malware"
    del db


def rmTempDB(test_object) -> None:
    """Cleanup the dbm database at tmp/tmp"""
    shutil.rmtree("tmp")
    os.chdir(test_object.initial_dir)
