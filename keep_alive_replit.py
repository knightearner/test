from deta import Deta

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


from flask import Flask, render_template, request

# app = Flask(__name__)

from threading import Thread

app = Flask('')

light_status = get_switch()


@app.route('/')
def index():
    return render_template('index.html', status=light_status)


@app.route('/switch_on')
def switch_on():
    global light_status
    light_status = update_switch_ON()
    return render_template('index.html', status=light_status)


@app.route('/switch_off')
def switch_off():
    global light_status
    light_status = update_switch_OFF()
    return render_template('index.html', status=light_status)


# if __name__ == '__main__':
#     app.run(debug=True)


def run():
  app.run(host="0.0.0.0", port=8000)


def keep_alive():
  server = Thread(target=run)
  server.start()
