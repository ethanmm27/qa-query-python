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

def blocker(col_one, col_two):
    mylist = []
    for a in get_all_reports(col_one, col_two):
        if is_yes(a.get("Blocker?")):
            mylist.append(a)
    write_report("List of all blocker bugs", mylist, "Blocker_Bugs_List.txt")

def user(user, col_one, col_two):
    mylist = []
    for a in get_all_reports(col_one, col_two):
        value = a.get("Test Owner")
        if isinstance(value, str) and value.lower().strip() == user.lower().strip():
            mylist.append(a)
    if mylist:
        fieldnames = []
        for entry in mylist:
            for key in entry.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
        with open('Final_CSV.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(mylist)
    write_report("List of all work done by " + user, mylist, "Work_Done_By_User.txt")

def repeatable_and_blocker(col_one, col_two):
    mylist = []
    for a in get_all_reports(col_one, col_two):
        if is_yes(a.get("Repeatable?")) and is_yes(a.get("Blocker?")):
            mylist.append(a)
    write_report("List of all repeatable and blocker bugs", mylist, "Repeatable_And_Blocker.txt")

def builddate(builddate, col_one, col_two):
    mylist = []
    builddatetime = pd.to_datetime(builddate)
    for a in get_all_reports(col_one, col_two):
        value = a.get("Build #")
        if isinstance(value, datetime) and value == builddatetime:
            mylist.append(a)
    write_report("List of all reports on build date " + builddate, mylist, "Build_Date_Reports.txt")

def findUsers(builddate, col_one, col_two):
    allUsers = []
    allUsersOnDate = []
    finalList = []
    builddatetime = pd.to_datetime(builddate)
    union_col = get_all_reports(col_one, col_two)
    for a in union_col:
        value = clean_name(a.get("Test Owner"))
        if value is not None and value not in allUsers:
            allUsers.append(value)
    for x in union_col:
        date = x.get("Build #")
        if isinstance(date, datetime) and date == builddatetime:
            owner = clean_name(x.get("Test Owner"))
            if owner is not None and owner not in allUsersOnDate:
                allUsersOnDate.append(owner)
    for y in allUsers:
        if y not in allUsersOnDate:
            finalList.append(y)
    write_report("List of all users that did not submit a report on " + builddate,
                 finalList, "Did_Not_Submit.txt")

def build_parser():
    parser = argparse.ArgumentParser(description='Parse and input data from a QA CSV into a database.')

    parser.add_argument('--load', action='store_true', dest='load',
                        help='Clear the collections and load the spreadsheets into the database first.')
    parser.add_argument('--file-one', default="EG4-DBDump_fall2026_c1.xlsx", dest='file_one',
                        help='Path to the first Excel file.')
    parser.add_argument('--file-two', default="EG4-DBDump_fall2026_c2.xlsx", dest='file_two',
                        help='Path to the second Excel file.')

    parser.add_argument('--blocker', action='store_true', dest='blocker',
                        help='Lists all blocker bugs.')
    parser.add_argument('--user', type=str,
                        help='Lists all work done by a user.')
    parser.add_argument('--repeatable', action='store_true', dest='repeatable',
                        help='Lists all repeatable bugs (use together with --blocker).')
    parser.add_argument('--builddate', type=str,
                        help='Lists all work done on a specific date.')
    parser.add_argument('--reportedUsers', action='store_true', dest='reportedUsers',
                        help='Lists all users who did not do work on a specific date (use with --builddate).')
    return parser