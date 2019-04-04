import json
import lxml
import praw
import requests
from bs4 import BeautifulSoup

def serialize_comment(comment):
  curr_comment = {}
  curr_comment["author"] = comment.author.name
  curr_comment["author_reply"] = None
  curr_comment["body"] = comment.body.encode('utf8')
  curr_comment["created_utc"] = comment.created_utc
  curr_comment["score"] = comment.score
  return curr_comment


def write_sample_to_file(num_posts, num_comments):
  reddit = praw.Reddit(client_id='wQaHdUWqKKgaLQ',
                       client_secret='mIDBYtZGLe_Pve7RiGcw2VWc-y4',
                       user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0')

  subs = []
  for submission in reddit.subreddit('depression').top('year', limit=num_posts):
    subs.append(submission)

  ret = []
  for i, submission in enumerate(subs):
    if i % 2000 == 0:
      f = open("year{}.txt".format(str(i)), "w+")
      json.dump(ret, f)
      f.close()
      ret = []

    if submission.author is None or submission.selftext_html is None:
      continue

    curr_submission = {}
    curr_submission["body"] = ""
    soup = BeautifulSoup(submission.selftext_html, 'lxml')
    for paragraph in soup.find_all("p"):
      curr_submission["body"] += paragraph.text

    curr_submission["author"] = submission.author.name
    curr_submission["created_utc"] = submission.created_utc
    curr_submission["title"] = submission.title.encode('utf8')
    curr_submission["url"] = submission.url
    curr_submission["upvote_ratio"] = submission.upvote_ratio

    print(i)
    print(curr_submission["title"])

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

    ret.append(curr_submission)
  f = open("year{}.txt".format(str(i)), "w+")
  json.dump(ret, f)
  f.close()

if __name__ == "__main__":
  write_sample_to_file(10, 30)
