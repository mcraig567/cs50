import cs50
import csv
from sys import argv, exit

#Check input arguements
if len(argv) != 2:
    print("Usage: roster.py House")
    exit(1)

#Create string for SQL to call
sql = "SELECT * FROM students WHERE house = '" + argv[1] + "' ORDER BY last ASC"

#Create connection to database and pull in requested data
db = cs50.SQL("sqlite:///students.db")
data = (db.execute(sql))

#Print requested data
for person in data:
    if person['middle'] != None:
        print("{} {} {}, born {}".format(person['first'], person['middle'], person['last'], person['birth']))
    else:
        print("{} {}, born {}".format(person['first'], person['last'], person['birth']))
