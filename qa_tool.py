import pymongo
import pandas as pd
import argparse
import csv
from bson import json_util
from datetime import datetime
import getpass
import os
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_database():
    uri = os.environ.get("MONGODB_URI")
    db_name = "mydatabase"
    if not uri:
        print("Enter your MongoDB connection details.")
        host = input("Cluster host (e.g. mycluster.abc123.mongodb.net): ").strip()
        host = host.replace("mongodb+srv://", "").replace("mongodb://", "").strip("/")
        username = input("Username: ").strip()
        password = getpass.getpass("Password (hidden): ")
        db_name = input("Database name [mydatabase]: ").strip() or "mydatabase"
        uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@{host}/"
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=8000)
    try:
        client.admin.command("ping")
    except pymongo.errors.PyMongoError as err:
        raise SystemExit(f"Could not connect to the database: {err}")
    return client[db_name]

def readin_database(file, collection):
    mylist = []
    for i in range(0, len(file)):
        row = file.iloc[i].to_dict()
        mylist.append(row)
    if mylist:
        collection.insert_many(mylist)