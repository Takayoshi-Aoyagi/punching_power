import datetime
import os
import smbus
import threading
import time
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import *
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


class Application(Frame):

    def __init__(self, master=None):
        self._master = master
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

        t1 = threading.Thread(target=self.init_measurement)
        t1.start()

    def set_status(self, status):
        label = 'STATUS: {}'.format(status)
        self.status_label.config(text=label)

    def create_widgets(self):
        self.status_label = Label(self)
        self.status_label.pack()
        self.set_status('Initializing...')

    def adjust(self):
        self.set_status("Now Adjusting offset...")
        time.sleep(5)
        gx, gy, gz, ax, ay, az, t = self.mpu.get_values()
        self.mpu.set_offset(-gx, -gy, -gz, -ax, -ay, -az)
        self.set_status("Adjusting offset Done")

    def measure(self):
        self.set_status('Measuring...')
        t = []
        y = []
        for a in range(1000):
            #os.system('clear')
            gx, gy, gz, ax, ay, az, temp = self.mpu.get_values()
            print(self.mpu.gx0, self.mpu.gy0, self.mpu.gz0)
            print 'Gyro X= %6d' % gx
	    print 'Gyro Y= %6d' % gy
	    print 'Gyro Z= %6d' % gz
	    print 'Acc. X= %6d' % ax
	    print 'Acc. Y= %6d' % ay
	    print 'Acc. Z= %6d' % az
	    print 'Temp. = %6.2f' % temp
            t.append(datetime.now())
            y.append(az)
	    #time.sleep(0.5)
        self.set_status('Measuring DONE')
        return t, y

    def plot(self, t, y):
        self.set_status('Plotting...')
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
        plt.plot(t, y)
        plt.gcf().autofmt_xdate()
        
        canvas = FigureCanvasTkAgg(fig, master=self._master)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.set_status('Plotting DONE')
        sec = 10
        for i in range(sec):
            self.set_status('Next measurement will start in {} sec.'.format(sec - i))
            time.sleep(1)
        
        canvas.get_tk_widget().pack_forget()
        
    def init_measurement(self):
        self.mpu = MPU6050()

        while True:
            self.adjust()
            t, y = self.measure()
            self.plot(t, y)

        
if __name__ == '__main__':
    root = Tk()
    root.title('Punching power')
    root.geometry('800x600')
    app = Application(master=root)
    app.mainloop()
    #root.destroy()
    
    sys.exit(1)

        
