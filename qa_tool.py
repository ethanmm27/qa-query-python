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

def get_all_reports(col_one, col_two):
    return list(col_one.aggregate([{"$unionWith": {"coll": col_two.name}}]))

def is_yes(value):
    return isinstance(value, str) and value.lower().strip() in ("yes", "y")

def clean_name(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.strip()
    return value if value != "" else None

def write_report(header, results, filename):
    with open(filename, "w") as file:
        file.write(header + ":\n")
        file.write("Total entries: ")
        file.write(str(len(results)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(results, indent=4))
    print("Total entries:", len(results))
