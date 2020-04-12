import csv
import cs50
from sys import argv, exit

#Check input arguements
if len(argv) != 2:
    print("Usage: import.py data.csv")
    exit(1)

#Initialize SQL connection
db = cs50.SQL("sqlite:///students.db")

#Set up counter for ID (key parameter)
id = 1

#Import data from .csv one row at a time
with open (argv[1], "r") as file:
    reader = csv.DictReader(file, delimiter = ",")
    for row in reader:

        #Check for middle name and set middle name to NULL if none
        name = row["name"].split()
        if len(name) == 2:
            first = name[0]
            middle = None
            last = name[1]

        else:
            first = name[0]
            middle = name[1]
            last = name[2]

        #Add data to database and increment user ID by one
        db.execute("INSERT INTO students(id, first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?, ?)",
            id, first, middle, last, row["house"], row["birth"])
        id += 1
