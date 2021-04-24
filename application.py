import threading
import time
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Frame, Label, Tk

#from MPU6050 import MPU6050
from motiontracker import MotionTracker



class ApplicationFrame(Frame):

    def __init__(self, master=None, bd_addr=None):
        self.terminate_flag = False
        self._master = master
        self.bd_addr = bd_addr
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

        self.tm = threading.Thread(target=self.init_measurement)
        self.tm.start()

    def terminate(self):
        self.session.stop_read_data()
        self.terminate_flag = True
        self.tm.join()
        self.destroy()

    def set_status(self, status):
        label = 'STATUS: {}'.format(status)
        print(label)
        self.status_label.config(text=label)

    def create_widgets(self):
        self.status_label = Label(self)
        self.status_label.pack()
        self.set_status('Initializing...')

    def adjust(self):
        self.count_down('Now Adjusting offset... {}', 5)

        gx, gy, gz, ax, ay, az, t = self.mpu.get_values()
        self.mpu.set_offset(-gx, -gy, -gz, -ax, -ay, -az)
        self.set_status("Adjusting offset Done")

    def measure(self):
        self.set_status('Measuring...')
        t = []
        y = []
        for a in range(1000):
            time.sleep(0.01)
            az = self.session.acc_z
            t.append(datetime.now())
            y.append(abs(az))
        self.set_status('Measuring DONE')
        return t, y

    def plot(self, t, y):
        self.set_status('Plotting...')
        fig, ax = plt.subplots()
        print(1)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
        print(2)
        plt.plot(t, y)
        plt.gcf().autofmt_xdate()
        print(3)
        ymax = max(y)
        tmax = t[y.index(ymax)]
        ax.annotate('MAX: {}'.format(ymax),
                   xy=(tmax, ymax), xytext=(tmax, ymax+5),
                   arrowprops=dict(facecolor='black', shrink=0.05),)
        print(4)
        
        canvas = FigureCanvasTkAgg(fig, master=self._master)
        print(5)
        canvas.draw()
        print(6)
        canvas.get_tk_widget().pack()
        self.set_status('Plotting DONE')

        self.count_down('Next measurement will be started in {} sec.', 10)
        
        canvas.get_tk_widget().pack_forget()

    def count_down(self, fmt, sec):
        for i in range(sec):
            self.set_status(fmt.format(sec - i))
            time.sleep(1)
        
    def init_measurement(self):
        print('Start: init_measurement')
        self.session = MotionTracker(bd_addr=self.bd_addr)
        print('start: start_read_data')
        self.session.start_read_data()
        print('started: start_read_data')

        while self.terminate_flag is False:
            # TODO
            #self.adjust()
            t, y = self.measure()
            print(t, y)
            self.plot(t, y)


class Application:

    def __init__(self, bd_addr=None):
        root = Tk()
        root.title('Punching power')
        #root.attributes('-fullscreen', True)
        root.geometry('800x600')
        frame = ApplicationFrame(master=root, bd_addr=bd_addr)
        frame.mainloop()
        self.frame = frame

    def destroy(self):
        try:
            self.frame.terminate()
        except Exception as e:
            print(e)
