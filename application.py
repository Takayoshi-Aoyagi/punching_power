import os
import threading
import time
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Button, Frame, Label, Tk
from tkinter.font import Font

#from MPU6050 import MPU6050
from motiontracker import MotionTracker


HISTORY_SIZE = 5


class ValueFrame(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.history = [0] * HISTORY_SIZE

        self.status_label = Label(self)
        self.status_label.pack()

        self.history_label = Label(self)
        self.history_label.pack(side='right')
        self.set_history(0)

        self.current_max_label = Label(self)
        self.current_max_font = Font(size=16)
        self.current_max_label['font'] = self.current_max_font
        self.current_max_label.pack(side='left')
        self.set_current_max(0)

    def set_status(self, status, color='black'):
        label = 'STATUS: {}'.format(status)
        print(label)
        self.status_label.config(text=label, fg=color)

    def set_history(self, value):
        self.history.insert(0, value)
        self.history = self.history[0:HISTORY_SIZE]
        text = 'history: ' + '  '.join(map(lambda x: '%.2f' % x, self.history))
        print(text)
        self.history_label.config(text=text)

    def set_current_max(self, ymax):
        text = 'max: %.2f' % ymax
        self.current_max_label.config(text=text)
        self.set_history(ymax)
        

class GraphFrame(Frame):

    def __init__(self, master=None, app_frame=None):
        super().__init__(master)
        self.app_frame=app_frame

    def plot(self, t, y, ymax):
        fig, ax = plt.subplots()
        print(1)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
        print(2)
        plt.plot(t, y)
        plt.gcf().autofmt_xdate()
        print(3)
        tmax = t[y.index(ymax)]
        ax.annotate('MAX: {}'.format(ymax),
                   xy=(tmax, ymax), xytext=(tmax, ymax+5),
                   arrowprops=dict(facecolor='black', shrink=0.05),)
        print(4)
        
        canvas = FigureCanvasTkAgg(fig, master=self)
        print(5)
        canvas.draw()
        print(6)
        canvas.get_tk_widget().pack()

        self.app_frame.count_down('Next measurement will be started in {} sec.', 10)
        
        canvas.get_tk_widget().pack_forget()


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

    def create_widgets(self):
        self.value_frame = ValueFrame(master=self._master)
        self.value_frame.pack()
        self.value_frame.set_status('Initializing...', color='red')

        self.graph_frame = GraphFrame(master=self._master,
                                      app_frame=self)
        self.graph_frame.pack()

    def adjust(self):
        self.count_down('Now Adjusting offset... {}', 5)

        gx, gy, gz, ax, ay, az, t = self.mpu.get_values()
        self.mpu.set_offset(-gx, -gy, -gz, -ax, -ay, -az)
        self.value_frame.set_status("Adjusting offset Done")

    def measure(self):
        self.value_frame.set_status('Measuring...', color='green')
        t = []
        y = []
        for a in range(1000):
            time.sleep(0.01)
            az = self.session.acc_z
            t.append(datetime.now())
            y.append(abs(az))
        self.value_frame.set_status('Measuring DONE')
        return t, y

    def count_down(self, fmt, sec):
        for i in range(sec):
            self.value_frame.set_status(fmt.format(sec - i))
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
            ymax = max(y)
            self.value_frame.set_current_max(ymax)
            self.graph_frame.plot(t, y, ymax)


class Application:

    def __init__(self, bd_addr=None):
        root = Tk()
        self.root = root
        root.title('Punching power')
        root.geometry('800x600')
        root.attributes('-fullscreen', True)
        root.bind("<F11>", self.quit_full_screen)
        frame = ApplicationFrame(master=root, bd_addr=bd_addr)
        frame.mainloop()
        self.frame = frame

    def quit_full_screen(self, event):
        self.root.attributes('-fullscreen', False)

    def destroy(self):
        try:
            self.frame.terminate()
        except Exception as e:
            print(e)
