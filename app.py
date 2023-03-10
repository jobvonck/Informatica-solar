from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "SolarShit"
socketio = SocketIO(app, cors_allowed_origins="*")

relays = {"R0": 0, "R1": 1, "R2": 1,"R3": 1,"R4": 1,"R5": 1,"R6": 1,"R7": 1}

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

def background_thread():
    while True:
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit('UpdateSensorData', {'Solar': dummy_sensor_value, "Battery": dummy_sensor_value, "Usage": dummy_sensor_value, "date": get_current_datetime()})
        socketio.sleep(5)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    global thread
    print("Client connected")

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


@socketio.on("GPIO")
def Handle_GPIO(data):
    print("Client clicked, pin =", relays[data["relay"]], data["state"])
    pin = relays[data["relay"]]
    if data["state"] == "ON":
        print("turning on", pin)
    elif data["state"] == "OFF":
        print("turning off", pin)


if __name__ == "__main__":
    socketio.run(app)
