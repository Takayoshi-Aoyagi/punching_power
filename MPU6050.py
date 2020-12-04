import smbus
import time

import RPi.GPIO as GPIO


class MPU6050:

    DevAdr = 0x68
    myBus = ""
    if GPIO.RPI_INFO['P1_REVISION'] == 1:
        myBus = 0
    else:
        myBus = 1
    b = smbus.SMBus(myBus)

    def __init__(self):
        self.gx0 = 0
        self.gy0 = 0
        self.gz0 = 0
        self.ax0 = 0
        self.ay0 = 0
        self.az0 = 0
        self.b.write_byte_data(self.DevAdr, 0x6B, 0x80) # RESET
	time.sleep(0.25)
	self.b.write_byte_data(self.DevAdr, 0x6B, 0x00) # RESET
        time.sleep(0.25)
        self.b.write_byte_data(self.DevAdr, 0x6A, 0x07) # RESET
        time.sleep(0.25)
	self.b.write_byte_data(self.DevAdr, 0x6A, 0x00) # RESET
	time.sleep(0.25)
	self.b.write_byte_data(self.DevAdr, 0x1A, 0x00) # CONFIG
	self.b.write_byte_data(self.DevAdr, 0x1B, 0x18) # +-2000/s
	self.b.write_byte_data(self.DevAdr, 0x1C, 0x10) # +-8g

    def set_offset(self, gx0, gy0, gz0, ax0, ay0, az0):
        print("set offset ", gx0, gy0, gz0, ax0, ay0, az0)
        self.gx0 = gx0
        self.gy0 = gy0
        self.gz0 = gz0
        self.ax0 = ax0
        self.ay0 = ay0
        self.az0 = az0
    
    def getValueGX(self):
	#self.b.write_byte(self.DevAdr, 0x43) #
        return self.getValue(0x43) + self.gx0
        
    def getValueGY(self):
	return self.getValue(0x45) + self.gy0

    def getValueGZ(self):
	return self.getValue(0x47) + self.gz0

    def getValueAX(self):
	#self.b.write_byte(self.DevAdr, 0x3B) #
	return self.getValue(0x3B) + self.ax0

    def getValueAY(self):
	return self.getValue(0x3D) + self.ay0

    def getValueAZ(self):
	return self.getValue(0x3F) + self.az0

    def getValueTemp(self):
	val = self.getValue(0x41)
	return (val/340.00+36.53)

    def getValue(self, adr):
	tmp = self.b.read_byte_data(self.DevAdr, adr)
	sign = tmp & 0x80
	tmp = tmp & 0x7F
	tmp = tmp<<8
	tmp = tmp | self.b.read_byte_data(self.DevAdr, adr+1)
	print '%4x' % tmp # debug
        
	if sign > 0:
	    tmp = tmp - 32768
            
	return tmp

    def get_values(self):
        gx = self.getValueGX()
        gy = self.getValueGY()
        gz = self.getValueGZ()
        ax = self.getValueAX()
        ay = self.getValueAY()
        az = self.getValueAZ()
        t = self.getValueTemp()
        return gx, gy, gz, ax, ay, az, t
