import json

with open('authors.txt', 'r') as f:
  authors = json.loads(f.read())

def get_total_num_posts(authors):
  num_posts = 0
  for author_id in authors:
    author_info = authors[author_id]
    num_posts += len(author_info)
  return num_posts

def get_average_body_vs(authors):
  '''
  Get average vader sentiment score across all posts.
  '''
  total_body_vs = 0
  num_posts = 0

  for author_id in authors:
    author_info = authors[author_id]
    num_posts += len(author_info)
    for post in author_info:
      body_vs = post['body_vs'][0]
      compound_vs = body_vs['compound']
      total_body_vs += compound_vs
  
  # Divide by number of posts to get average sentiment score
  avg_body_vs = total_body_vs / num_posts
  return avg_body_vs

def get_slope_info(authors):
  '''
  Get average slope of posts for a user.
  NOTE: We only looks at users that have more than one post.
  '''
  num_multi_posts_users = 0
  total_slope = 0
  min_slope = float("inf")
  max_slope = -float("inf")

  for author_id in authors:
    author_info = authors[author_id]
    has_multi_post = len(author_info) > 1 
    if not has_multi_post:
      continue

    num_multi_posts_users += 1
    slope = get_slope(author_info)
    if slope < min_slope:
      min_slope = slope
    if slope > max_slope:
      max_slope = slope
    total_slope += slope
  avg_slope = total_slope / num_multi_posts_users
  return min_slope, max_slope, avg_slope

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
  total_comment_vs = 0
  total_author_vs = 0
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
      total_comment_vs += comment_vs 
      total_author_vs += author_vs 
  total_num_posts = get_total_num_posts(authors)
  avg_comment_vs = total_comment_vs / total_num_posts
  avg_author_vs = total_author_vs / total_num_posts
  return avg_comment_vs, avg_author_vs


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

def get_avg_comments_min_max(authors, min_slope, max_slope):
  range_value = 0.1 
  num_min_slopes = 0
  max_min_comments = 0
  num_max_slopes = 0
  max_max_comments = 0
  for author_id in authors:
    author_info = authors[author_id]
    slope = get_slope(author_info)
    max_num_comments = get_max_num_comments(author_info)
    if slope >= min_slope and slope <= min_slope + range_value:
      num_min_slopes += 1
      max_min_comments += max_num_comments
    elif slope >= max_slope - range_value and slope <= max_slope:
      num_max_slopes += 1
      max_max_comments += max_num_comments
  avg_min_comments = max_min_comments / num_min_slopes
  avg_max_comments = max_max_comments / num_min_slopes
  return avg_min_comments, avg_max_comments


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

# Average body vs score over all posts
avg_body_vs = get_average_body_vs(authors)
output.append('Average Body VS: {}'.format(avg_body_vs))

# Slope of line of best fit of the body vs score over all of a user's posts
min_slope, max_slope, avg_slope = get_slope_info(authors)
output.append('Minimum Slope: {}, Maximum Slope: {}, Average Slope: {}'.format(min_slope, max_slope, avg_slope))

# Average comment vs score COMPARED to average author vs score (per post)
avg_comment_vs, avg_author_vs = get_avg_comment_author(authors)
output.append('Average Comment VS score: {}, Average Author VS score: {}'.format(avg_comment_vs, avg_author_vs))

# Number of positive body vs scores COMPARED to number of negative body vs scores
num_positive, num_neutral, num_negative = get_pos_neu_neg_body(authors)
output.append('Number positive body vs scores: {}, Number neutral body vs scores: {}, Number negative body vs scores: {}'.format(num_positive, num_neutral, num_negative))

# Average number of comments for users with slopes [min_slope, min_slope + 0.1] 
# COMPARED to Average number of comments for users with slopes [max_slope - 0.1, max_slope]
avg_min_comments, avg_max_comments = get_avg_comments_min_max(authors, min_slope, max_slope)
output.append('Average maximum number comments in a post for users with low slopes: {}, Average maximum number comments in a post for users with high slopes: {}'.format(avg_min_comments, avg_max_comments))

f = open('analytics.txt', 'w+')
for out in output:
  print(out)
  f.write('{}\n'.format(out))
f.close()
