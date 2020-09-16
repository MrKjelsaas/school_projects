import re

file = open("canvas.txt", "r")
fileString = file.read()

# Find and print student emails
studentEmails = re.findall("s\d{6}@oslomet.no", fileString)
print(studentEmails)

# Find all emails
emails = re.findall("[\w\.]+@[\w\.-]+", fileString)
print(emails)

# Find the last activity of all students
lastActivities = re.findall("\d{1,2} [A-Z][a-z]{2} at \d{1,2}:\d{2}", fileString)
print(lastActivities)

# Find the sys ids of the students
sysIDs = re.findall("fs:\d{3}:\d+", fileString)
print(sysIDs)

# Find the total activity time of the users on Canvas
totalActivityTimes = re.findall("\n(\d{2}:\d{2}:*\d*)", fileString)
print(totalActivityTimes)

# Find the names of the Students
studentNames = re.findall("\n([a-zA-Z]+[ -][a-zA-Z]+[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*)\t[a-z]", fileString)
print(studentNames)

# Find all users with name where the user activity was more than 10 hours
studentsWithActivityMoreThan10Hours = re.findall("\n([a-zA-Z]+[ -][a-zA-Z]+[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*)\t[a-z].*?\n.*?\n.*?\n.*?\n[1-9]\d\d*:\d{2}:\d{2}", fileString)
print(studentsWithActivityMoreThan10Hours)

# Find all users with name where the last user login was in August
studentsWhereLastLoginWasInAugust = re.findall("\n([a-zA-Z]+[ -][a-zA-Z]+[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*[ -]*[a-zA-Z]*)\t[a-z].*?\n.*?\n.*?\n.*?Aug", fileString)
print(studentsWhereLastLoginWasInAugust)
