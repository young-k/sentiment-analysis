from datetime import datetime
from collections import defaultdict
import json
import statistics

import graphs

with open('final.txt', 'r') as f:
  final = json.loads(f.read())

def get_posts_per_day(final):
  day_posts = defaultdict(int)
  for post in final:
    created_utc = post['created_utc']
    created_date = datetime.utcfromtimestamp(created_utc)
    month_day = '{},{}'.format(created_date.month, created_date.day)
    day_posts[month_day] += 1
  posts_per_day = []
  num_posts = day_posts.values()
  avg_num_posts = statistics.mean(num_posts)
  std_dev_num_posts = statistics.stdev(num_posts)
  return avg_num_posts, std_dev_num_posts

def get_posts_per_user(final):
  user_posts = defaultdict(int)
  for post in final:
    author = post['author']
    user_posts[author] += 1
  num_posts = user_posts.values()
  avg_num_posts = statistics.mean(num_posts)
  std_dev_num_posts = statistics.stdev(num_posts)
  max_num_posts = max(num_posts)
  min_num_posts = min(num_posts)
  return avg_num_posts, std_dev_num_posts, max_num_posts, min_num_posts

def get_upvote_ratio(final):
  upvote_ratio = []
  for post in final:
    upvote = post['upvote_ratio'] 
    upvote_ratio.append(upvote)
  avg_upvote = statistics.mean(upvote_ratio)
  std_dev_upvote = statistics.stdev(upvote_ratio)
  return avg_upvote, std_dev_upvote

############
#  GRAPHS  #
############

def plot_posts_per_day(final):
  day_posts = defaultdict(int)
  for post in final:
    created_utc = post['created_utc']
    created_date = datetime.utcfromtimestamp(created_utc)
    month_day = '{},{}'.format(created_date.month, created_date.day)
    day_posts[month_day] += 1
  X = list(range(len(day_posts)))
  Y = list(day_posts.values())
  graphs.plot_bar_graph(X, Y, 'Number of Posts Per Day')

# Uncomment the following lines to generate each graph
plot_posts_per_day(final)

###########
# RESULTS #
###########

output = []

avg_num_posts_per_day, std_dev_num_posts_per_day = get_posts_per_day(final)
output.append('Average/Std Dev number of posts per day: {}, {}'.format(avg_num_posts_per_day, std_dev_num_posts_per_day))

avg_num_posts_per_user, std_dev_num_posts_per_user, max_num_posts_per_user, min_num_posts_per_user = get_posts_per_user(final)
output.append('Average/Std Dev/Max/Min number of posts per user: {}, {}, {}, {}'.format(avg_num_posts_per_user, std_dev_num_posts_per_user, max_num_posts_per_user, min_num_posts_per_user))

avg_upvote_ratio, std_dev_upvote_ratio = get_upvote_ratio(final)
output.append('Average/Std Dev upvote ratio: {}, {}'.format(avg_upvote_ratio, std_dev_upvote_ratio))

f = open('final_analytics.txt', 'w+')
for out in output:
  print(out)
  f.write('{}\n'.format(out))
f.close()
