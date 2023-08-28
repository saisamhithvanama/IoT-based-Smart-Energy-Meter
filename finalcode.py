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
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Informative print statement to indicate module loading
print("All Modules Loaded ...... ")

class MyDb(object):
    def __init__(self, Table_Name='iot'):
        # Initialize the DynamoDB resource and table
        self.Table_Name = Table_Name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)
        self.client = boto3.client('dynamodb')
        
    @property
    def get(self):
        # Retrieve data from DynamoDB using the given key
        d = datetime.datetime.now()
        _Date = "{}-{}-{}".format(d.month, d.day, d.year)
        _Time = "{}:{}:{}".format(d.hour, d.minute, d.second)
        response = self.table.get_item(
            Key={
                'Sensor_Id': "1"
            }
        )
        return response
    
    def put(self, Sensor_Id='', Current='', Power=''):
        # Insert data into DynamoDB table
        self.table.put_item(
            Item={
                'Sensor_Id': Sensor_Id,
                'Current': Current,
                'Power': Power
            }
        )
        
    def delete(self, Sensor_Id=','):
        # Delete data from DynamoDB table using the given key
        self.table.delete_item(
            Key={
                'Sensor_Id': Sensor_Id
            }
        )
        
    def describe_table(self):
        # Retrieve details about the DynamoDB table
        response = self.client.describe_table(
            TableName='iot'
        )
        return response
    
    @staticmethod
    def sensor_value():
        sum = 0
        GAIN = 4
        
        # Loop for data collection and calculations
        for x in range(200):
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c, gain=GAIN)
            chan = AnalogIn(ads, ADS.P0, ADS.P1)
            current0 = abs(abs(chan.value) * 0.001)
            current1 = round(current0, places)
            sum = sum + ((current1) * (current1))
            
        avg = (math.sqrt(sum / 200))
        avg1 = round(avg, places)
        power0 = abs(220 * avg)
        power1 = round(power0, places)
        current = Decimal(str(avg1))
        power = Decimal(str(power1))
        
        return current, power

def main(counter):
    # Start a new thread for periodic execution
    threading.Timer(interval=10, function=main, args=(counter,)).start()
    obj = MyDb()
    Current, Power = obj.sensor_value()
    obj.put(Sensor_Id=str(counter), Current=str(Current), Power=str(Power))
    counter += 1
    print("Uploaded Sample on Cloud C:{}, P:{}".format(Current, Power))

if __name__ == "__main__":
    counter = 0
    main(counter)
