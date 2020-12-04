import sys

from Tkinter import Tk

from application import Application


if __name__ == '__main__':
    exit_code = 0
    root = None
    try:
        root = Tk()
        #root.attributes('-fullscreen', True)
        root.title('Punching power')
        root.geometry('800x600')
        app = Application(master=root)
        app.mainloop()
    except Exception as e:
        print(e)
        exit_code = 1
    finally:
        if root:
            root.destroy()
        sys.exit(exit_code)
