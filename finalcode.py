try:
    import os
    import sys
    import datetime
    import time
    import boto3
    import threading
    from decimal import Decimal
    from adafruit_bus_device.i2c_device import I2CDevice
    from adafruit_seesaw.seesaw import Seesaw
    from board import SCL, SDA
    import board
    import busio
    import math
    import json
    import logging
    import argparse
   # import Adafruit_ADS1x15
   # from Adafruit_IO import *
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    print("All Modules Loaded ...... ")
except Exception as e:
    print("Error {143}".format(e))
    GAIN = 4
    samples = 200
    places = int(2)
    # i2c_bus = busio.I2C(board.SCL, board.SDA)
    # adc1 = ADS.ADS1115()
class MyDb(object):
    def __init__(self,Table_Name='iot'):
        self.Table_Name=Table_Name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)
        self.client = boto3.client('dynamodb')
    @property
    def get(self):
        d = datetime.datetime.now()
        _Date = "{}-{}-{}".format(d.month, d.day, d.year)
        _Time = "{}:{}:{}".format(d.hour, d.minute, d.second)
        response = self.table.get_item(
            Key={
                'Sensor_Id':"1"
            }
        )
        return response
    def put(self, Sensor_Id='' , Current='', Power=''):
        self.table.put_item(
            Item={
                'Sensor_Id':Sensor_Id,
                'Current':Current,
                'Power' : Power
            }
        )
    def delete(self, Sensor_Id=','):
        self.table.delete_item(
            Key={
                'Sensor_Id': Sensor_Id
            }
        )
    def describe_table(self):
        response = self.client.describe_table(
            TableName='iot'
        )
        return response
    @staticmethod
    def sensor_value():
        count = int(0)
 ads = 0
        places = int(2)
        sum = 0
        GAIN = 4
        #ADS1115.setGain(GAIN_FOUR)
        for x in range(200):
            i2c=busio.I2C(board.SCL, board.SDA)
            ads=ADS.ADS1115(i2c,gain=GAIN)
            chan=AnalogIn(ads, ADS.P0, ADS.P1)
            current0 = abs(abs(chan.value)*0.001)
            current1 = round(current0, places)
            sum=sum+((current1)*(current1))
        avg = (math.sqrt(sum/200))
        avg1 = round(avg, places)
        power0 = abs(220*avg)
        power1 = round(power0, places)
        current = Decimal(str(avg1))
        power = Decimal(str(power1))
        print('avg:',avg)
        print('curent:',current)
        print('power:',power)
        #return Decimal(str(current)), Decimal(str(power))
        return current, power
def main():
    global counter
    counter = 0
    threading.Timer(interval=10, function=main).start()
    obj = MyDb()
    Current , Power = obj.sensor_value()
    obj.put(Sensor_Id=str(counter), Current=str(Current), Power=str(Power))
    counter = counter + 1
    print("Uploaded Sample on Cloud C:{},P:{} ".format(Current, Power))
if __name__ == "__main__":
    main()


