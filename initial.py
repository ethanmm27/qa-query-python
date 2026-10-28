import pymongo
import pandas as pd
import argparse
import csv
from bson import json_util
from datetime import datetime

myclient = pymongo.MongoClient()
# placeholder for db details
mydb = myclient["mydatabase"]

parser = argparse.ArgumentParser(description='Parse and input data from a QA CSV into a database.')

def readin_database(file, collection):
    mylist = []
    for i in range(0, len(file)):
        dict = file.iloc[i].to_dict()
        mylist.append(dict)

    x = collection.insert_many(mylist)

col_one = mydb["FileOne"]
col_two = mydb["FileTwo"]
file_one = pd.read_excel("EG4-DBDump_fall2026_c1.xlsx", header=0)
file_two = pd.read_excel("EG4-DBDump_fall2026_c2.xlsx", header=0)

readin_database(file_one, col_one)
readin_database(file_two, col_two)

parser.add_argument('--blocker', action='store_true', dest='blocker',
                    help='Lists all blocker bugs.')
def blocker(col_one, col_two):
    mylist = []
    union_col = col_one.aggregate([{ "$unionWith": { "coll": col_two.name} }])
    for a in union_col:
        value = a.get("Blocker?")
        if isinstance(value, str) and value.lower().strip() in ("yes", "y"):
            mylist.append(a)
    with open("DB_Answers_2.txt", "w") as file:
        file.write("List of all blocker bugs:\n")
        file.write("Total entries: ")
        file.write(str(len(mylist)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(mylist, indent=4))
    print("Total entries:", len(mylist))

parser.add_argument('--user', type=str,
                    help='Lists all work done by a user.')
def user(user, col_one, col_two):
    mylist = []
    union_col = col_one.aggregate([{ "$unionWith": { "coll": col_two.name} }])
    for a in union_col:
        value = a.get("Test Owner")
        if isinstance(value, str) and value.lower().strip() in user.lower():
            mylist.append(a)
    with open('Final_CSV.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=mylist[0].keys())
        writer.writeheader()
        writer.writerows(mylist)
    with open("DB_Answers_1.txt", "w") as file:
        file.write("List of all work done by ")
        file.write(user)
        file.write(":\n")
        file.write("Total entries: ")
        file.write(str(len(mylist)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(mylist, indent=4))
    print("Total entries:", len(mylist))

parser.add_argument('--repeatable', action='store_true', dest='repeatable',
                    help='Lists all repeatable bugs.')

def repeatable_and_blocker(col_one, col_two):
    mylist = []
    union_col = col_one.aggregate([{ "$unionWith": { "coll": col_two.name} }])
    for a in union_col:
        value_one = a.get("Repeatable?")
        value_two = a.get ("Blocker?")
        if isinstance(value_one, str) and value_one.lower().strip() in ("yes", "y"):
            if isinstance(value_two, str) and value_two.lower().strip() in ("yes", "y"):
                mylist.append(a)
    with open("DB_Answers_3.txt", "w") as file:
        file.write("List of all repeatable and blocker bugs:\n")
        file.write("Total entries: ")
        file.write(str(len(mylist)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(mylist, indent=4))
    print("Total entries:", len(mylist))

parser.add_argument('--builddate', type=str,
                    help='Lists all work done on a specific date.')
def builddate(builddate, col_one, col_two):
    mylist = []
    builddatetime = pd.to_datetime(builddate)
    union_col = col_one.aggregate([{ "$unionWith": { "coll": col_two.name} }])
    for a in union_col:
        value = a.get("Build #")
        if isinstance(value, datetime) and value == builddatetime:
            mylist.append(a)
    with open("DB_Answers_4.txt", "w") as file:
        file.write("List of all reports on build date ")
        file.write(builddate)
        file.write(":\n")
        file.write("Total entries: ")
        file.write(str(len(mylist)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(mylist, indent=4))
    print("Total entries:", len(mylist))

parser.add_argument('--reportedUsers', action='store_true', dest='reportedUsers',
                    help='Lists all users who did not do work on a specific date.')
def findUsers(builddate, col_one, col_two):
    allUsers = []
    allUsersOnDate = []
    finalList = []
    builddatetime = pd.to_datetime(builddate)
    union_col = list(col_one.aggregate([{ "$unionWith": { "coll": col_two.name} }]))
    for a in union_col:
        value = a.get("Test Owner")
        if value is not None and not pd.isna(value):
            if isinstance(value, str):
                value = value.strip()
            if value != "" and value not in allUsers:
                allUsers.append(value)
    for x in union_col:
        date = x.get("Build #")
        if isinstance(date, datetime) and date == builddatetime:
            owner = x.get("Test Owner")
            if owner is not None and not pd.isna(owner):
                if isinstance(owner, str):
                    owner = owner.strip()
                if owner != "" and owner not in allUsersOnDate:
                    allUsersOnDate.append(owner)
    for y in allUsers:
        if y not in allUsersOnDate:
            finalList.append(y)
    with open("DB_Answers_5.txt", "w") as file:
        file.write("List of all users that did not submit a report on ")
        file.write(builddate)
        file.write(":\n")
        file.write("Total entries: ")
        file.write(str(len(finalList)))
        file.write("\n")
        file.write("\n")
        file.write(json_util.dumps(finalList, indent=4))
    print("Total entries:", len(finalList))

args = parser.parse_args()
if args.repeatable and args.blocker:
    repeatable_and_blocker(col_one, col_two)
elif args.blocker:
    blocker(col_one, col_two)
elif args.user:
    user(args.user, col_one, col_two)
elif args.builddate and args.reportedUsers:
    findUsers(args.builddate, col_one, col_two)
elif args.builddate:
    builddate(args.builddate, col_one, col_two)