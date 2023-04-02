from flask import Flask, render_template, request
from flask_socketio import SocketIO
from datetime import datetime
from threading import Lock
import time
from helpers import (
    FrankEnergy,
    CalcBat,
    GetWeather,
    GetHighestPrice,
    CheckPrice,
    DeleteFilecontent,
    SaveData,
    CalculateWh,
)

# from sensorTest import TestSensors as Sensor

import RPi.GPIO as GPIO
from sensor import Sensor

lastPrice = []
lastSensorData = {"date": [], "Solar": [], "Battery": [], "Usage": []}

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
    GPIO.setmode(GPIO.BCM)
    for i in relays:
        GPIO.setup(int(relays[i]["pin"]), GPIO.OUT)
        GPIO.output(int(relays[i]["pin"]), GPIO.HIGH)

stad = "Gemeente Groningen"

sensor = Sensor()

minCharge = 20
maxCharge = 90

overide = False


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S").split()[1]


def background_thread():
    DeleteFilecontent()
    BatteryProd = 0
    SolarProd = 0
    lastCalc = 10

    while True:
        data = sensor.GetData()
        charge = CalcBat(data["BatteryVoltage"])

        SaveData(data["SolarPower"], data["BatteryPower"])

        if lastCalc == 12:
            lastCalc = 0
            SolarProd, BatteryProd = CalculateWh()
            print(SolarProd, BatteryProd)
        else:
            lastCalc += 1

        socketio.emit(
            "UpdateSensorData",
            {
                "Solar": data["SolarPower"],
                "Battery": data["BatteryPower"],
                "BatteryVoltage": data["BatteryVoltage"],
                "BatteryCurrent": data["BatteryCurrent"],
                "BatteryProduction": BatteryProd,
                "SolarVoltage": data["SolarVoltage"],
                "SolarCurrent": data["SolarCurrent"],
                "SolarProduction": SolarProd,
                "Usage": data["Usage"],
                "Price": FrankEnergy()[0:2],
                "Charge": charge,
                "date": get_current_datetime(),
            },
        )

        if len(lastSensorData) >= 50:
            if i in lastSensorData:
                lastSensorData[i].pop(0)
        lastSensorData["date"].append(get_current_datetime())
        lastSensorData["Solar"].append(data["SolarPower"])
        lastSensorData["Battery"].append(data["BatteryPower"])
        lastSensorData["Usage"].append(data["Usage"])

        if (
            (CheckPrice() and relays["R7"]["state"] != "on" and charge > minCharge)
            or (charge > maxCharge and relays["R7"]["state"] != "on")
        ) and not overide:
            pin = int(relays["R7"]["pin"])
            GPIO.output(pin, GPIO.LOW)
            relays["R7"]["state"] = "on"
            socketio.emit("UpdateButtons", {"Relay": "R7", "State": "on"})
            print("Stroomteruglevering aan")
        elif (
            (CheckPrice() and charge <= minCharge and relays["R7"]["state"] != "off")
            or (charge <= maxCharge and relays["R7"]["state"] != "off")
        ) and not overide:
            pin = int(relays["R7"]["pin"])
            GPIO.output(pin, GPIO.HIGH)
            relays["R7"]["state"] = "off"
            socketio.emit("UpdateButtons", {"Relay": "R7", "State": "off"})
            print("Stroomteruglevering uit")

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
    socketio.emit("UpdatePrice", FrankEnergy()[2])
    for i in relays:
        socketio.emit("UpdateButtons", {"Relay": i, "State": relays[i]["state"]})
    socketio.emit("DataGraph", lastSensorData)


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
    socketio.run(app, host='0.0.0.0')
    GPIO.cleanup()
