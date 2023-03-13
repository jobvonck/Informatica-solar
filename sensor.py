import board
import busio
import adafruit_ina219

class DataColector:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_ina219.INA219(i2c)
        sensor1 = adafruit_ina219.INA219(i2c)
    
    def DataSensors():
        return None
