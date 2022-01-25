"""Helper functions to write url data from plaintext files to databases"""

import dbm.dumb as dbm
import typing
import os
from pymongo import MongoClient


def preprocess_urls_from_file(filename) -> typing.List[str]:
    """Prepare urls for entry to database from raw form

    Basically just strips url fragments, may need to do more later
    """
    with open(filename, "r") as fin:
        evil_urls = fin.readlines()
    return [url.strip().split("#")[0] for url in evil_urls]


def create_dbm_database(source: str, dest: str, reason: bytes):
    """Load sample data to a dbm database.

    Creates dbm if it doesn't exist, inserts if it exists (overwriting repeated entries)
    dbm databases are local flat files, no setup is necessary!

    :param source: source plaintext filename with 1 url entry per line (input)
    :param dest: destination dbm filename with
    :param reason: "reason" this record is unsafe
    """
    evil_urls = preprocess_urls_from_file(source)
    with dbm.open(dest, "c", 0o666) as db:
        for url in evil_urls:
            db[url] = reason


def create_mongo_database(
    source: str, dest: str, reason: str, conn: str, username: str, password: str
):
    """Load sample data to a mongodb database

    Creates database if it doesn't exist, inserts if it exists (overwriting repeated entries)
    Note: MongoDB server must be running and accessible via the connection string!

    :param source: source plaintext filename with 1 url entry per line (input)
    :param dest: destination database to create or add to
    :param reason: "reason" this record is unsafe
    :param conn: connection string to mongodb instance
    :param username: mongodb username
    :param password: mongodb password
    """
    evil_urls = preprocess_urls_from_file(source)
    evil_urls_documents = map(lambda x: {"url": x, "reason": reason}, evil_urls)

    mongo = MongoClient(
        conn,
        username=username,
        password=password,
        authSource="admin",
        authMechanism="SCRAM-SHA-256",
    )[dest][dest]
    mongo.insert_many(evil_urls_documents)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print("Creating dbm databases..", end=" ")
    create_dbm_database("unsafe_urls.txt", "unsafe", b"unsafe")
    create_dbm_database("sample.txt", "sample", b"known malware")
    print("Done.")

    print("Creating mongo databases..", end=" ")
    if (
        "MONGO_INITDB_ROOT_USERNAME" in os.environ
        and "MONGO_INITDB_ROOT_PASSWORD" in os.environ
    ):
        username = os.environ["MONGO_INITDB_ROOT_USERNAME"]
        password = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    else:
        username, password = "root", "example"

    try:
        create_mongo_database(
            source="mongo_sample.txt",
            dest="urlinfo_sample",
            reason="known malware - mongo!",
            conn="mongodb://localhost:27017/",
            username="root",
            password="example",
        )
        create_mongo_database(
            source="mongo_unsafe_urls.txt",
            dest="urlinfo_unsafe",
            reason="suspected malware, admin blocking",
            conn="mongodb://localhost:27017/",
            username="root",
            password="example",
        )
    except:
        raise ConnectionError(
            "Couldn't connect to Mongo.\n"
            "Check that it is running and your environment variables are set properly:\n"
            "\tMONGO_INITDB_ROOT_USERNAME=<your-mongo-username>\n"
            "\tMONGO_INITDB_ROOT_PASSWORD=<your-mongo-password>"
        )
    print("Done.")
