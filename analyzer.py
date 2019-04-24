import json
import statistics

with open('authors.txt', 'r') as f:
  authors = json.loads(f.read())

def get_total_num_posts(authors):
  num_posts = 0
  for author_id in authors:
    author_info = authors[author_id]
    num_posts += len(author_info)
  return num_posts

def get_body_vs_data(authors):
  '''
  Get average vader sentiment score across all posts.
  '''
  body_vs_data = []

  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      body_vs = post['body_vs'][0]
      compound_vs = body_vs['compound']
      body_vs_data.append(compound_vs)
  
  # Divide by number of posts to get average sentiment score
  avg = statistics.mean(body_vs_data)
  std_dev = statistics.stdev(body_vs_data)
  return avg, std_dev

def get_slope_info(authors):
  '''
  Get average slope of posts for a user.
  NOTE: We only looks at users that have more than one post.
  '''
  slope_data = []
  min_slope = float("inf")
  max_slope = -float("inf")

  for author_id in authors:
    author_info = authors[author_id]
    has_multi_post = len(author_info) > 1 
    if not has_multi_post:
      continue

    slope = get_slope(author_info)
    slope_data.append(slope)
    if slope < min_slope:
      min_slope = slope
    if slope > max_slope:
      max_slope = slope
  avg_slope = statistics.mean(slope_data)
  std_dev_slope = statistics.stdev(slope_data)
  return min_slope, max_slope, avg_slope, std_dev_slope

def get_slope(author_info):
  # This helper was taken from Stack Overflow: 
  # https://stackoverflow.com/questions/22239691/code-for-best-fit-straight-line-of-a-scatter-plot-in-python
  def best_fit_slope(X, Y):
      xbar = sum(X)/len(X)
      ybar = sum(Y)/len(Y)
      n = len(X) # or len(Y)

      numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
      denum = sum([xi**2 for xi in X]) - n * xbar**2

      y_intercept = numer / denum
      slope = ybar - y_intercept * xbar
      return slope
  X = []
  Y = []
  for index, post in enumerate(author_info):
    body_vs = post['body_vs'][0]
    compound_vs = body_vs['compound']
    X.append(index)
    Y.append(compound_vs)
  slope = best_fit_slope(X, Y)
  return slope



def get_avg_comment_author(authors):
  comment_data = []
  author_data = []
  for author_id in authors:
    author_info = authors[author_id]
    comment_vs = 0
    author_vs = 0
    for post in author_info:
      all_comment_vs = post['all_comment_vs']
      all_author_vs = post['all_author_vs']
      for comment_info in all_comment_vs:
        comment_vs += comment_info['compound']
      for reply_info in all_author_vs:
        author_vs += reply_info['compound']
      if len(all_comment_vs) > 0:
        comment_vs /= len(all_comment_vs)
      if len(all_author_vs) > 0:
        author_vs /= len(all_author_vs)
      comment_data.append(comment_vs)
      author_data.append(author_vs)
  avg_comment_vs = statistics.mean(comment_data)
  avg_author_vs = statistics.mean(author_data)
  std_comment_vs = statistics.stdev(comment_data)
  std_author_vs = statistics.stdev(author_data)
  return avg_comment_vs, avg_author_vs, std_comment_vs, std_author_vs


def get_pos_neu_neg_body(authors):
  num_positive = 0
  num_neutral = 0
  num_negative = 0
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      body_vs = post['body_vs'][0]['compound']
      if body_vs > 0:
        num_positive += 1
      elif body_vs < 0:
        num_negative += 1
      else:
        num_neutral += 1
  return num_positive, num_neutral, num_negative

def get_comments_min_max(authors, min_slope, max_slope, std_dev_slope):
  min_comments_data = []
  max_comments_data = []
  for author_id in authors:
    author_info = authors[author_id]
    slope = get_slope(author_info)
    max_num_comments = get_max_num_comments(author_info)
    if slope >= min_slope and slope <= min_slope + std_dev_slope:
      min_comments_data.append(max_num_comments)
    elif slope >= max_slope - std_dev_slope and slope <= max_slope:
      max_comments_data.append(max_num_comments)
  avg_min_comments = statistics.mean(min_comments_data)
  avg_max_comments = statistics.mean(max_comments_data)
  std_dev_min_comments = statistics.stdev(min_comments_data)
  std_dev_max_comments = statistics.stdev(max_comments_data)
  return avg_min_comments, avg_max_comments, std_dev_min_comments, std_dev_max_comments


def get_max_num_comments(author_info):
  max_num_comments = 0
  for post in author_info:
    num_comments = len(post['all_comment_vs'])
    if num_comments > max_num_comments:
      max_num_comments = num_comments
  return max_num_comments


def get_avg_num_comments(author_info):
  num_comments = 0
  for post in author_info:
    num_comments += len(post['all_comment_vs'])
  num_posts = len(author_info)
  avg_comments = num_comments / num_posts
  return avg_comments

###########
# RESULTS #
###########

output = []

# Total number of posts
total_num_posts = get_total_num_posts(authors)
output.append('Total Number of posts: {}'.format(total_num_posts))

# Body vs score data over all posts
avg_body_vs, std_dev_body_vs = get_body_vs_data(authors)
output.append('Average Body VS: {}, Standard Dev Body VS: {}'.format(avg_body_vs, std_dev_body_vs))

# Slope of line of best fit of the body vs score over all of a user's posts
min_slope, max_slope, avg_slope, std_dev_slope = get_slope_info(authors)
output.append('Minimum Slope: {}, Maximum Slope: {}, Average Slope: {}, Standard Dev Slope: {}'.format(min_slope, max_slope, avg_slope, std_dev_slope))

# Comment vs score data COMPARED to author vs score data (per post)
avg_comment_vs, avg_author_vs, std_comment_vs, std_author_vs = get_avg_comment_author(authors)
output.append('Average/Standard Dev Comment VS score: {}/{}, Average/Standard Dev Author VS score: {}/{}'.format(avg_comment_vs, std_comment_vs, avg_author_vs, std_author_vs))

# Number of positive body vs scores COMPARED to number of negative body vs scores
num_positive, num_neutral, num_negative = get_pos_neu_neg_body(authors)
output.append('Number positive body vs scores: {}, Number neutral body vs scores: {}, Number negative body vs scores: {}'.format(num_positive, num_neutral, num_negative))

# Number of comments for users with slopes [min_slope, min_slope + std_dev_slope] 
# COMPARED to number of comments for users with slopes [max_slope -std_dev_slope, max_slope]
avg_min_comments, avg_max_comments, std_dev_min_comments, std_dev_max_comments = get_comments_min_max(authors, min_slope, max_slope, std_dev_slope)
output.append('Average/Standard Dev maximum number comments in a post for users with low slopes: {}/{}, Average/Standard Dev maximum number comments in a post for users with high slopes: {}/{}'.format(avg_min_comments, std_dev_min_comments, avg_max_comments, std_dev_max_comments))

f = open('analytics.txt', 'w+')
for out in output:
  print(out)
  f.write('{}\n'.format(out))
f.close()
