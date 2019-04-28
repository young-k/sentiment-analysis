import os

import plotly.tools as tools
import plotly.plotly as py
import plotly.graph_objs as go

tools.set_credentials_file(username=os.environ['PLOTLY_USERNAME'], api_key=os.environ['PLOTLY_API_KEY'])

def plot_bar_graph(x, y, title):
  bar = go.Bar(x=x, y=y)
  data = [bar]
  layout = go.Layout(title=title)
  figure = go.Figure(data=data, layout=layout)
  filename = title.replace(' ', '_').lower()
  py.plot(figure, filename=filename)

def plot_scatter_graph(x, y, title, lines=True):
  if lines:
    mode = 'lines+markers'
  else:
    mode = 'markers'
  scatter = go.Scatter(
    x=x,
    y=y,
    mode=mode,
  )
  data = [scatter]
  layout = go.Layout(title=title)
  figure = go.Figure(data=data, layout=layout)
  filename = title.replace(' ', '_').lower()
  py.plot(figure, filename=filename)
