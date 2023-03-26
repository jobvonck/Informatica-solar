from flask import Flask, render_template, request
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
import time
from helpers import FrankEnergy, CalcBat, GetWeather


thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "SolarShit"
socketio = SocketIO(app, cors_allowed_origins="*")


relays = {
    "R0": {"pin": 17, "state": "off"},
    "R1": {"pin": 18, "state": "off"},
    "R2": {"pin": 27, "state": "off"},
    "R3": {"pin": 22, "state": "off"},
    "R4": {"pin": 23, "state": "off"},
    "R5": {"pin": 24, "state": "off"},
    "R6": {"pin": 25, "state": "off"},
    "R7": {"pin": 5, "state": "off"},
}

state = "running"
if state != "DEBUG":
    import RPi.GPIO as GPIO

    from sensorTest import TestSensors as sensor

    GPIO.setmode(GPIO.BCM)
    for i in relays:
        GPIO.setup(int(relays[i]["pin"]), GPIO.OUT)
        GPIO.output(int(relays[i]["pin"]), GPIO.HIGH)
else:
    from sensorTest import TestSensors as sensor

stad = "Groningen"

sensor = sensor()


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S").split()[1]


def background_thread():
    while True:
        data = sensor.GetData()
        socketio.emit(
            "UpdateSensorData",
            {
                "Solar": data["Power2"],
                "Battery": data["Power1"],
                "Usage": data["Usage"],
                "Price": FrankEnergy(),
                "Charge": CalcBat(data["BatteryVoltage"]),
                "date": get_current_datetime(),
            },
        )
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
    socketio.emit("GetWeather", GetWeather(stad))
    for i in relays:
        socketio.emit("UpdateButtons", {"Relay": i, "State": relays[i]["state"]})


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


@socketio.on("GPIO")
def Handle_GPIO(data):
    pin = int(relays[data["relay"]]["pin"])
    state = relays[data["relay"]]["state"]
    if state != data["state"]:
        if data["state"] == "on":
            print("turning on", pin)
            GPIO.output(pin, GPIO.LOW)
            relays[data["relay"]]["state"] = "on"
            socketio.emit("UpdateButtons", {"Relay": data["relay"], "State": "on"})
        elif data["state"] == "off":
            print("turning off", pin)
            GPIO.output(pin, GPIO.HIGH)
            relays[data["relay"]]["state"] = "off"
            socketio.emit("UpdateButtons", {"Relay": data["relay"], "State": "off"})
    socketio.sleep(10)


if __name__ == "__main__":
    socketio.run(app)
    GPIO.cleanup()
