from deta import Deta
import pandas as pd
import plotly.graph_objs as go
from flask import Flask, render_template, request
from threading import Thread
from datetime import *
import pytz

key='d0p3jsxc_jAhdkSrj194KPkx9YX8iDRZzZCBKQPfP'

def get_switch():
    deta = Deta(key)
    users = deta.Base("switch")
    fetch_res = users.fetch({"key": "ua1hy6g6qak6"})
    return fetch_res.items[0]['Switch']

def update_switch_OFF():
    deta = Deta(key)
    users = deta.Base("switch")
    users.update(
    {
      'Switch': 'OFF'
    }, 'ua1hy6g6qak6')
    
    fetch_res = users.fetch({"key": "ua1hy6g6qak6"})
    return fetch_res.items[0]['Switch']

def update_switch_ON():
    deta = Deta(key)
    users = deta.Base("switch")
    users.update(
    {
      'Switch': 'ON'
    }, 'ua1hy6g6qak6')
    
    fetch_res = users.fetch({"key": "ua1hy6g6qak6"})
    return fetch_res.items[0]['Switch']


def get_graph_data():
  deta = Deta(key)
  users = deta.Base("option_sell_db")
  df=users.fetch().items
  df=pd.DataFrame(df)
  df['DateTime'] = pd.to_datetime(df.DateTime)
  df=df.sort_values(by='DateTime', ascending=True)
  today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
  today_data = df[df['DateTime'].dt.date == today]  
  
  today_data.Profit=today_data.Profit.apply(float)
  # print(today_data)

  return today_data['DateTime'].to_list(),today_data.Profit.to_list()


app = Flask('')

light_status = get_switch()

graph_json={}

@app.route('/')
def index():
    global graph_json

    x,y=get_graph_data()
    data = pd.DataFrame({'x': x,'y': y,})
    graph = go.Figure(
        data=[go.Scatter(x=data['x'], y=data['y'], mode='lines')],
        layout=go.Layout(title='Sample Graph', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))
    )

    # Convert the Plotly graph to JSON
    graph_json = graph.to_json()
    # print(graph_json)
    return render_template('index.html', status=light_status,graph_json=graph_json)


@app.route('/switch_on')
def switch_on():
    global light_status
    light_status = update_switch_ON()
    return render_template('index.html', status=light_status,graph_json=graph_json)


@app.route('/switch_off')
def switch_off():
    global light_status
    light_status = update_switch_OFF()
    return render_template('index.html', status=light_status,graph_json=graph_json)


# if __name__ == '__main__':
#     app.run(debug=True)


def run():
  app.run(host="0.0.0.0", port=8000)


def keep_alive():
  server = Thread(target=run)
  server.start()
