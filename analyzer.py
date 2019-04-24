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

def get_average_slope(authors):
  '''
  Get average slope of posts for a user.
  NOTE: We only looks at users that have more than one post.
  '''
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
  
  num_multi_posts_users = 0
  total_slope = 0

  for author_id in authors:
    author_info = authors[author_id]
    has_multi_post = len(author_info) > 1 
    if not has_multi_post:
      continue

    num_multi_posts_users += 1
    X = []
    Y = []
    for index, post in enumerate(author_info):
      body_vs = post['body_vs'][0]
      compound_vs = body_vs['compound']
      X.append(index)
      Y.append(compound_vs)
    slope = best_fit_slope(X, Y)
    total_slope += slope
  avg_slope = total_slope / num_multi_posts_users
  return avg_slope

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


# Total number of posts
total_num_posts = get_total_num_posts(authors)
print('Total Number of posts: {}'.format(total_num_posts))

# Average body vs score over all posts
avg_body_vs = get_average_body_vs(authors)
print('Average Body VS: {}'.format(avg_body_vs))

# Slope of line of best fit of the body vs score over all of a user's posts
avg_slope = get_average_slope(authors)
print('Average Slope: {}'.format(avg_slope))

# Average comment vs score COMPARED to average author vs score (per post)
avg_comment_vs, avg_author_vs = get_avg_comment_author(authors)
print('Average Comment VS score: {}, Average Author VS score: {}'.format(avg_comment_vs, avg_author_vs))

# Number of positive body vs scores COMPARED to number of negative body vs scores
num_positive, num_neutral, num_negative = get_pos_neu_neg_body(authors)
print('Number positive body vs scores: {}, Number neutral body vs scores: {}, Number negative body vs scores: {}'.format(num_positive, num_neutral, num_negative))

#f = open('authors.txt', 'w+')
#json.dump(authors, f)
#f.close()
