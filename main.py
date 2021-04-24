import os
import sys

from application import Application


if __name__ == '__main__':
    app = None
    exit_code = 0
    try:
        bd_addr = os.environ.get('BT_DEVICE_ADDR') or '20:20:10:26:24:79'
        print(f'bd_addr={bd_addr}')
        app = Application(bd_addr)
    except Exception as e:
        print(e)
        exit_code = 1
    finally:
        if app:
            app.destroy()
        sys.exit(exit_code)
