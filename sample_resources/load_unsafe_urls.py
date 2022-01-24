"""Write evil_url_list to dbm.dumb database

This file exist in case the dbm databases need to be made in a different format or be remade
"""

import dbm.dumb as dbm


def create_dbm_database(source: str, dest: str, reason: bytes):
    with open(source, "r") as fin:
        evil_urls = fin.readlines()
    with dbm.open(dest, "c", 0o666) as db:
        for url in evil_urls:
            clean_url = url.strip().split("#")[0]
            db[clean_url] = reason


if __name__ == "__main__":
    create_dbm_database("unsafe_urls.txt", "unsafe", b"unsafe")
    create_dbm_database("sample.txt", "sample", b"known malware")
