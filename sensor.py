import board
import busio
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from random import random, randrange

class Sensors:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor1 = INA219(self.i2c)
        self.sensor2 = INA219(self.i2c)

        self.sensor1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor1.bus_voltage_range = BusVoltageRange.RANGE_16V

        self.sensor2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        self.sensor2.bus_voltage_range = BusVoltageRange.RANGE_16V
    def GetData(self):
        self.bus_voltage = self.sensor1.bus_voltage  # voltage on V- (load side)
        self.shunt_voltage = self.sensor1.shunt_voltage  # voltage between V+ and V- across the shunt
        self.voltage = self.bus_voltage + self.shunt_voltage
        
        self.power1 = self.sensor1.power  # power in watts
        self.power2 = self.sensor2.power  # power in watts

        self.usage = self.power2-self.power1
        return {'BatteryVoltage': self.voltage, 'Power1': self.power1, 'Power2' : self.power2, 'Usage':self.usage}