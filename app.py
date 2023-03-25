from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
import time

thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "SolarShit"
socketio = SocketIO(app, cors_allowed_origins="*")

relays = {"R0": {"pin" : 17, "state" : "on"}, "R1": {"pin" : 18, "state" : "on"}, "R2": {"pin" : 27, "state" : "on"},"R3": {"pin" : 22, "state" : "on"},"R4": {"pin" : 23, "state" : "on"},"R5": {"pin" : 24, "state" : "on"},"R6": {"pin" : 25, "state" : "on"},"R7": {"pin" : 5, "state" : "on"}}

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S").split()[1]

def background_thread():
    while True:
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit('UpdateSensorData', {'Solar': round(random() * 100, 3), "Battery": round(random() * 100, 3), "Usage": round(random() * 100, 3), "date": get_current_datetime()})
        socketio.sleep(5)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buttons")
def buttons():
    return render_template("buttons.html")

@socketio.on("connect")
def connect():
    global thread
    print("Client connected")

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("StartButtons")
def StartButtons():
    for i in relays:
        socketio.emit("UpdateButtons", {"Relay": i, "State": relays[i]["state"]})


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


@socketio.on("GPIO")
def Handle_GPIO(data):
    pin = relays[data["relay"]]["pin"]
    state = relays[data["relay"]]["state"]
    if state != data["state"]:
        if data["state"] == "on":
            print("turning on", pin)
            relays[data["relay"]]["state"] = "on"
            socketio.emit("UpdateButtons", {"Relay": data["relay"], "State": "on"})
        elif data["state"] == "off":
            print("turning off", pin)
            relays[data["relay"]]["state"] = "off"
            socketio.emit("UpdateButtons", {"Relay": data["relay"], "State": "off"})
    socketio.sleep(10)
            


if __name__ == "__main__":
    socketio.run(app)
