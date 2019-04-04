import json
import operator
import re

with open('testing.txt', 'r') as f:
  submissions = json.loads(f.read())

authors = {}

for submission in submissions:
  if submission['author'] in authors:
    authors[submission['author']] += 1
  else:
    authors[submission['author']] = 1

sorted_x = sorted(authors.items(), key=operator.itemgetter(1))
print(sorted_x)
