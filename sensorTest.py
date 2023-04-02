from random import random, randrange


class TestSensors:
    def __init__(self):
        pass

    def GetData(self):
        self.power1 = round(random() * 100, 1)
        self.power2 = round(random() * 100, 1)

        self.voltage1 = randrange(1163, 1289) / 100
        self.voltage2 = 12
        self.current1 = round(self.power1 / self.voltage1, 2)
        self.current2 = round(self.power2 / self.voltage2, 2)

        self.usage = abs(self.power1 - self.power2)

        return {
            "BatteryVoltage": self.voltage1,
            "SolarVoltage": self.voltage2,
            "BatteryCurrent": self.current1,
            "SolarCurrent": self.current2,
            "BatteryPower": self.power1,
            "SolarPower": self.power2,
            "Usage": self.usage,
        }
