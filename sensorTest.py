from random import random, randrange

class TestSensors:
    def __init__(self):
        pass
    def GetData(self):
        self.power1 = round(random() * 100, 3)
        self.power2 = round(random() * 100, 3)

        self.usage = self.power2-self.power1

        return {'BatteryVoltage': round(randrange(1163, 1289) / 100, 3), 'Power1': self.power1, 'Power2' : self.power2, 'Usage':self.usage}