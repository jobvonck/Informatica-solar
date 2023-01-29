from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

relays = {'R0':0, 'R1':0}

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

def background_thread():
    print("Generating random sensor values")
    while True:
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit('updateNumber', {'value': dummy_sensor_value})
        socketio.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

@socketio.on('GPIO')
def Handle_GPIO(data):
    print('Client clicked, pin =', relays[data['relay']], data['state'])
    pin = relays[data['relay']]
    if data['state'] == 'ON':
        print("turning on", pin)
    elif data['state'] == 'OFF':
        print("turning off", pin)

if __name__ == '__main__':
    socketio.run(app)