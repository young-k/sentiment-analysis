import json

with open('authors.txt', 'r') as f:
  authors = json.loads(f.read())

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


avg_body_vs = get_average_body_vs(authors)
print('Average Body VS: {}'.format(avg_body_vs))

avg_slope = get_average_slope(authors)
print('Average Slope: {}'.format(avg_slope))

#f = open('authors.txt', 'w+')
#json.dump(authors, f)
#f.close()
