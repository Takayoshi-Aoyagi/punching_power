import threading
import time
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import Frame, Label, Tk

from MPU6050 import MPU6050


class ApplicationFrame(Frame):

    def __init__(self, master=None):
        self.terminate_flag = False
        self._master = master
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

        self.tm = threading.Thread(target=self.init_measurement)
        self.tm.start()

    def terminate(self):
        self.terminate_flag = True
        self.tm.join()
        self.destroy()

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

        ymax = max(y)
        tmax = t[y.index(ymax)]
        ax.annotate('MAX: {}'.format(ymax),
                   xy=(tmax, ymax), xytext=(tmax, ymax+5),
                   arrowprops=dict(facecolor='black', shrink=0.05),)
        
        canvas = FigureCanvasTkAgg(fig, master=self._master)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.set_status('Plotting DONE')
        sec = 10
        for i in range(sec):
            self.set_status('Next measurement will be started in {} sec.'.format(sec - i))
            time.sleep(1)
        
        canvas.get_tk_widget().pack_forget()
        
    def init_measurement(self):
        self.mpu = MPU6050()

        while self.terminate_flag is False:
            self.adjust()
            t, y = self.measure()
            self.plot(t, y)


class Application:

    def __init__(self):
        root = Tk()
        root.title('Punching power')
        #root.attributes('-fullscreen', True)
        root.geometry('800x600')
        frame = ApplicationFrame(master=root)
        frame.mainloop()
        self.frame = frame

    def destroy(self):
        try:
            self.frame.terminate()
        except Exception as e:
            print(e)
