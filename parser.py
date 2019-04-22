from collections import defaultdict
import json
import operator
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

with open('final.txt', 'r') as f:
  submissions = json.loads(f.read())

# find authors with at least 2 submissions
authors = {}
for submission in submissions:
  if submission['author'] in authors:
    authors[submission['author']] += 1
  else:
    authors[submission['author']] = 1

multiple_post_authors = set()
for author, num_submissions in authors.items():
  if num_submissions > 1:
    multiple_post_authors.add(author)

print('RUNNING COMPUTATIONS')

# now do computations on those authors
submissions = [s for s in submissions if s['author'] in multiple_post_authors]

all_title_vs = []
all_body_vs = []

authors = {}
for submission in submissions:
  body_vs = analyzer.polarity_scores(submission['body'])
  title_vs = analyzer.polarity_scores(submission['title'])

  all_body_vs.append(body_vs)
  all_title_vs.append(title_vs)

  all_comment_vs = []
  all_author_vs = []
  for comment in submission['top_comments']:
    comment_vs = analyzer.polarity_scores(comment['body'])
    all_comment_vs.append(comment_vs)
    if comment['author_reply']:
      author_vs = analyzer.polarity_scores(comment['author_reply']['body'])
      all_author_vs.append(comment_vs)

  if submission['author'] in authors:
    authors[submission['author']].append({
        'body_vs': [body_vs],
        'title_vs': [title_vs],
        'all_comment_vs': all_comment_vs,
        'all_author_vs': all_author_vs,
    })
  else:
    authors[submission['author']] = [{
        'body_vs': [body_vs],
        'title_vs': [title_vs],
        'all_comment_vs': all_comment_vs,
        'all_author_vs': all_author_vs,
    }]

print('POST PROCESSING')
print(authors)

f = open('authors.txt', 'w+')
json.dump(authors, f)
f.close()
