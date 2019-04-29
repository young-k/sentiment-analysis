from collections import defaultdict
import json
import statistics

import graphs
from scipy.stats import linregress
import plotly.plotly as py
import plotly.graph_objs as go

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
    num_comments = len(post['all_comment_vs']) + len(post['all_author_vs'])
    if num_comments > max_num_comments:
      max_num_comments = num_comments
  return max_num_comments


def get_avg_num_comments(author_info):
  num_comments = []
  for post in author_info:
    num_comments.append(len(post['all_comment_vs']) + len(post['all_author_vs']))
  avg_comments = statistics.mean(num_comments)
  return avg_comments

def get_comments_per_post(authors):
  num_comments = []
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      num_comments.append(len(post['all_comment_vs']) + len(post['all_author_vs']))
  avg_comments = statistics.mean(num_comments)
  std_dev_comments = statistics.stdev(num_comments)
  return avg_comments, std_dev_comments

def get_comments_per_post_wo_zero(authors):
  num_comments = []
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      num_comment = len(post['all_comment_vs']) + len(post['all_author_vs'])
      if num_comment > 0:
        num_comments.append(num_comment)
  avg_comments = statistics.mean(num_comments)
  std_dev_comments = statistics.stdev(num_comments)
  return avg_comments, std_dev_comments

def get_user_comments(authors):
  user_comments = []
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      user_comments.append(len(post['all_author_vs']))
  avg_user_comments = statistics.mean(user_comments)
  std_dev_user_comments = statistics.stdev(user_comments)
  return avg_user_comments, std_dev_user_comments

def get_user_comments_wo_zero(authors):
  user_comments = []
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      num_user_comment = len(post['all_author_vs'])
      if num_user_comment > 0:
        user_comments.append(num_user_comment)
  avg_user_comments = statistics.mean(user_comments)
  std_dev_user_comments = statistics.stdev(user_comments)
  return avg_user_comments, std_dev_user_comments

############
#  GRAPHS  #
############

def print_linear_regression(X, Y, title):
  linear = linregress(X, Y)
  rval = linear.rvalue
  pval = linear.pvalue
  print('[Linear Regression for {}] r-value: {}, r-squared: {}, p-value: {}'.format(title, rval, rval**2, pval))


def plot_author_vs_num_comments(authors):
  info = defaultdict(list)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      all_author_vs = post['all_author_vs']
      num_comments = len(post['all_comment_vs']) + len(all_author_vs)
      for author_vs in all_author_vs:
        info[num_comments].append(author_vs['compound'])
  X = []
  Y = []
  for num_comments in info:
    X.append(num_comments)
    Y.append(statistics.mean(info[num_comments]))
  title = 'Author vs score VS Number of comments'
  print_linear_regression(X, Y, title)
  #graphs.plot_scatter_graph(X, Y, title)

def plot_body_vs_num_comments(authors):
  info = defaultdict(list)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      body_compound = post['body_vs'][0]['compound']
      num_comments = len(post['all_comment_vs']) + len(post['all_author_vs'])
      info[num_comments].append(body_compound)
  X = []
  Y = []
  for num_comments in info:
    X.append(num_comments)
    Y.append(statistics.mean(info[num_comments]))
  title = 'Author body score VS Number of comments'
  print_linear_regression(X, Y, title)
  #graphs.plot_scatter_graph(X, Y, title)

def plot_author_vs_comment_vs(authors):
  info = defaultdict(list)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      all_comment_vs = []
      for comment_vs in post['all_comment_vs']:
        all_comment_vs.append(comment_vs['compound'])
      if len(all_comment_vs) > 0:
        avg_comment_vs = statistics.mean(all_comment_vs)
        all_author_vs = post['all_author_vs']
        for author_vs in all_author_vs:
          info[avg_comment_vs].append(author_vs['compound'])
  X = []
  Y = []
  for avg_comment_vs in info:
    X.append(avg_comment_vs)
    Y.append(statistics.mean(info[avg_comment_vs]))
  title = 'Author vs score VS Average comment vs score'
  print_linear_regression(X, Y, title)
  #graphs.plot_scatter_graph(X, Y, title, lines=False)

def plot_author_vs_comment_vs(authors):
  info = defaultdict(list)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      all_comment_vs = []
      for comment_vs in post['all_comment_vs']:
        all_comment_vs.append(comment_vs['compound'])
      if len(all_comment_vs) > 0:
        avg_comment_vs = round_nearest(statistics.mean(all_comment_vs), 0.05)
        all_author_vs = post['all_author_vs']
        for author_vs in all_author_vs:
          info[avg_comment_vs].append(author_vs['compound'])
  X = []
  Y = []
  for avg_comment_vs in info:
    X.append(avg_comment_vs)
    Y.append(statistics.mean(info[avg_comment_vs]))
  title = 'Author vs score VS Average comment vs score'
  print_linear_regression(X, Y, title)
  #graphs.plot_scatter_graph(X, Y, 'Author vs score VS Average comment vs score', lines=False)

def plot_body_vs_comment_vs(authors):
  info = defaultdict(list)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      all_comment_vs = []
      for comment_vs in post['all_comment_vs']:
        all_comment_vs.append(comment_vs['compound'])
      if len(all_comment_vs) > 0:
        avg_comment_vs = round_nearest(statistics.mean(all_comment_vs), 0.05)
        body_vs = post['body_vs'][0]['compound']
        info[avg_comment_vs].append(body_vs)
  X = []
  Y = []
  for avg_comment_vs in info:
    X.append(statistics.mean(info[avg_comment_vs]))
    Y.append(avg_comment_vs)
  title = 'Average comment vs score VS Body vs score'
  print_linear_regression(X, Y, title)
  graphs.plot_scatter_graph(X, Y, title, lines=False)

def plot_slope_info(authors):
  '''
  Get average slope of posts for a user.
  NOTE: We only looks at users that have more than one post.
  '''
  slope_data = []
  slope_dict = defaultdict(int)

  for author_id in authors:
    author_info = authors[author_id]
    has_multi_post = len(author_info) > 1 
    if not has_multi_post:
      continue

    slope = round_nearest(get_slope(author_info), 0.05)
    slope_dict[slope] += 1
    slope_data.append(slope)
  avg_slope = statistics.mean(slope_data)
  std_dev_slope = statistics.stdev(slope_data)
  X = list(slope_dict.keys())
  Y = list(slope_dict.values())
  title = 'Frequency VS Slopes in Sentiment'
  graphs.plot_bar_graph(X, Y, title)

def plot_comment_sentiment(authors):
  info = defaultdict(int)
  for author_id in authors:
    author_info = authors[author_id]
    for post in author_info:
      for comment_vs in post['all_comment_vs']:
        comment_compound = round_nearest(comment_vs['compound'], 0.05)
        info[comment_compound] += 1
  X = list(info.keys())
  Y = list(info.values())
  title = 'Frequency VS Comment Sentiment'
  graphs.plot_bar_graph(X, Y, title)

def round_nearest(x, a):
  return round(x / a) * a

# Uncomment the line below to get the desired graph
#plot_author_vs_num_comments(authors)
#plot_body_vs_num_comments(authors)
#plot_author_vs_comment_vs(authors)
plot_body_vs_comment_vs(authors)
#plot_slope_info(authors)
#plot_comment_sentiment(authors)


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

avg_comments_per_post, std_dev_comments_per_post = get_comments_per_post(authors)
output.append('Average/Std Dev num comments per post: {}, {}'.format(avg_comments_per_post, std_dev_comments_per_post))

avg_comments_per_post_wo_zero, std_dev_comments_per_post_wo_zero = get_comments_per_post_wo_zero(authors)
output.append('Average/Std Dev num comments per post without zero: {}, {}'.format(avg_comments_per_post_wo_zero, std_dev_comments_per_post_wo_zero))

avg_user_comments, std_dev_user_comments = get_user_comments(authors)
output.append('Average/Std Dev num user comments on their own post: {}, {}'.format(avg_user_comments, std_dev_user_comments))

avg_user_comments_wo_zero, std_dev_user_comments_wo_zero = get_user_comments_wo_zero(authors)
output.append('Average/Std Dev num user comments on their own post without zero: {}, {}'.format(avg_user_comments_wo_zero, std_dev_user_comments_wo_zero))

f = open('authors_analytics.txt', 'w+')
for out in output:
  print(out)
  f.write('{}\n'.format(out))
f.close()
