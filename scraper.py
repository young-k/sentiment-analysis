import datetime
import json
import lxml
import praw
import requests
from bs4 import BeautifulSoup

data = []
#after_id = 't3_b9msry'
after_id = 't3_b9imfg'

def serialize_comment(comment):
  curr_comment = {}
  curr_comment["author"] = comment.author.name
  curr_comment["author_reply"] = None
  curr_comment["body"] = comment.body
  curr_comment["created_utc"] = comment.created_utc
  curr_comment["score"] = comment.score
  return curr_comment

def write_sample_to_file(num_posts, num_comments):
  reddit = praw.Reddit(client_id='wQaHdUWqKKgaLQ',
                       client_secret='mIDBYtZGLe_Pve7RiGcw2VWc-y4',
                       user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0')

  global after_id
  params = {'after': after_id}
  submissions = reddit.subreddit('depression').new(limit=num_posts, params=params)

  for submission in submissions:
    after_id = 't3_' + submission.id
    print(after_id)
    if submission.author is None or submission.selftext_html is None:
      continue

    curr_submission = {}
    curr_submission["body"] = ""
    soup = BeautifulSoup(submission.selftext_html, 'lxml')
    for paragraph in soup.find_all("p"):
      curr_submission["body"] += paragraph.text

    curr_submission["author"] = submission.author.name
    curr_submission["created_utc"] = submission.created_utc
    curr_submission["id"] = submission.id
    curr_submission["title"] = submission.title
    curr_submission["url"] = submission.url
    curr_submission["upvote_ratio"] = submission.upvote_ratio

    print(submission.title)

    submission.comment_sort = 'top'
    top_comments = submission.comments.list()

    real_comments = [comment for comment in top_comments \
        if isinstance(comment, praw.models.Comment)]
    real_comments = [comment for comment in real_comments \
        if comment.author is not None]
    real_comments.sort(key=lambda c: c.score, reverse=True)

    curr_submission["top_comments"] = []
    for comment in real_comments[:num_comments]:
      curr_comment = serialize_comment(comment)
      curr_submission["top_comments"].append(curr_comment)

      for reply in comment._replies:
        if isinstance(reply, praw.models.Comment) and \
            reply.author is not None:
          if reply.author.name == curr_submission["author"]:
            curr_comment["author_reply"] = serialize_comment(reply)

    data.append(curr_submission)

if __name__ == '__main__':
  #write_sample_to_file(None, 1, 40)
  #after_id = 't3_' + data[-1]['id']

  while True:
    counter = 1

    while len(data) < 200:
      print(len(data))
      print(after_id)
      write_sample_to_file(1000, 40)

    counter += 1
    f = open('./infinite/{}.txt'.format(str(counter)), 'w+')
    json.dump(data, f)
    f.close()
    data = []
