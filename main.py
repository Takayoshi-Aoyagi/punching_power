import sys

from application import Application


if __name__ == '__main__':
    app = None
    exit_code = 0
    try:
        app = Application()
    except Exception as e:
        print(e)
        exit_code = 1
    finally:
        if app:
            app.destroy()
        sys.exit(exit_code)
