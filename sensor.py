import board
import busio
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from random import random, randrange


class Sensor:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor2 = INA219(self.i2c, 0x40)
        self.sensor1 = INA219(self.i2c, 0x41)

        self.sensor1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor1.bus_voltage_range = BusVoltageRange.RANGE_16V

        self.sensor2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor2.bus_voltage_range = BusVoltageRange.RANGE_16V

    def GetData(self):
        self.bus_voltage1 = self.sensor1.bus_voltage  # voltage on V- (load side)
        self.shunt_voltage1 = self.sensor1.shunt_voltage  # voltage between V+ and V- across the shunt

        self.voltage1 = self.bus_voltage1 + self.shunt_voltage1
        self.voltage2 = self.bus_voltage + self.shunt_voltage

        self.current1 = self.sensor1.current/1000
        self.current2 = self.sensor2.current/1000

        self.power1 = self.sensor1.power  
        self.power2 = self.sensor2.power

        self.usage = self.power1 - self.power2
        return {
            "BatteryVoltage": self.voltage1,
            "SolarVoltage": self.voltage2,
            "BatteryCurrent": self.current1,
            "SolarCurrent": self.current2,
            "BatteryPower": self.power1,
            "SolarPower": self.power2,
            "Usage": abs(self.usage),
        }
