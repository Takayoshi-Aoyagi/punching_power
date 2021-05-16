import os
import threading
import time
from datetime import datetime

import matplotlib
import matplotlib.dates as mdates
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Button, Frame, Label, Tk, CENTER
from tkinter.font import Font

#from MPU6050 import MPU6050
from motiontracker import MotionTracker


HISTORY_SIZE = 5


class StatusFrame(Frame):

    def __init__(self, master=None):
        self._master = master
        super().__init__(master)
        self.status_font = Font(size=35)
        self.status_label = Label(self)
        self.status_label.configure(anchor='center')
        self.status_label.pack()
        
    def set_status(self, status, color='black'):
        text = 'STATUS: {}'.format(status)
        print(text)
        self.status_label.config(text=text, fg=color, font=self.status_font)


class ValueFrame(Frame):

    def __init__(self, master=None):
        self._master = master
        super().__init__(master)
        self.history = [0] * HISTORY_SIZE

        status_size, size = self.get_font_size()
        self.max_font = Font(size=70)
        self.font = Font(size=50)

        row = 0
        headers = ['MAX', 'hist1', 'hist2', 'hist3', 'hist4', 'hist5']
        for i, header in enumerate(headers):
            label = Label(self)
            label.config(text=header, font=self.font)
            label.grid(row=row, column=i)
        row = 1
        col = 0
        self.current_max_label = Label(self)
        self.current_max_label['font'] = self.max_font
        self.current_max_label.grid(row=row, column=col,
                                    padx=(50, 50))

        self.history_labels = []
        for i in range(HISTORY_SIZE):
            col += 1
            label = Label(self)
            label.grid(row=row, column=col, padx=(30, 30))
            self.history_labels.append(label)

        self.set_current_max(0)
        self.set_history(0)

    def get_font_size(self):
        width = self._master.winfo_screenwidth()
        if width > 2000:
            return 60, 100
        else:
            return 16, 20
        
    def set_history(self, value):
        self.history.insert(0, value)
        self.history = self.history[0:HISTORY_SIZE]
        #text = 'history: ' + '  '.join(map(lambda x: '%.2f' % x, self.history))
        #print(text)
        i = 0
        for val, label in zip(self.history, self.history_labels):
            i += 1
            text = '%.2f' % val
            label.config(text=text, fg='black', font=self.font)

    def set_current_max(self, ymax):
        text = '%.2f' % ymax
        self.current_max_label.config(text=text)
        self.set_history(ymax)
        

class GraphFrame(Frame):

    def __init__(self, master=None, app_frame=None):
        super().__init__(master)#, bg='cyan')
        self.app_frame=app_frame

    def plot(self, t, y, ymax):
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
        fig.set_size_inches(19.5, 7.5, forward=True)
        plt.plot(t, y)
        plt.gcf().autofmt_xdate()
        tmax = t[y.index(ymax)]
        ax.annotate('MAX: {}'.format(ymax),
                   xy=(tmax, ymax), xytext=(tmax, ymax+5),
                   arrowprops=dict(facecolor='black', shrink=0.05),)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, side='top', fill='both')

        self.app_frame.count_down('Next measurement will be started in {} sec.', 10)
        
        canvas.get_tk_widget().pack_forget()


class ApplicationFrame(Frame):

    def __init__(self, master=None, bd_addr=None):
        self.terminate_flag = False
        self._master = master
        self.bd_addr = bd_addr
        Frame.__init__(self, master)
        self.create_widgets()

        self.tm = threading.Thread(target=self.init_measurement)
        self.tm.start()

    def terminate(self):
        self.session.stop_read_data()
        self.terminate_flag = True
        self.tm.join()
        self.destroy()

    def create_widgets(self):
        self.status_frame = StatusFrame(master=self._master)
        self.status_frame.grid(row=0, column=0, pady=(30, 30))
        self.value_frame = ValueFrame(master=self._master)

        self.status_frame.set_status('Initializing...', color='red')
        self.value_frame.grid(row=1, column=0, sticky='s')
        self.graph_frame = GraphFrame(master=self._master,
                                      app_frame=self)
        self.graph_frame.grid(row=2, column=0)

    def adjust(self):
        self.count_down('Now Adjusting offset... {}', 5)

        gx, gy, gz, ax, ay, az, t = self.mpu.get_values()
        self.mpu.set_offset(-gx, -gy, -gz, -ax, -ay, -az)
        self.status_frame.set_status("Adjusting offset Done")

    def measure(self):
        self.status_frame.set_status('Measuring...', color='green')
        t = []
        y = []
        for a in range(1000):
            time.sleep(0.01)
            az = self.session.acc_z
            t.append(datetime.now())
            y.append(abs(az))
        self.status_frame.set_status('Measuring DONE')
        return t, y

    def count_down(self, fmt, sec):
        for i in range(sec):
            self.status_frame.set_status(fmt.format(sec - i))
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
