import atexit
from aparat_dl import App

if __name__ == "__main__":
    app = App()
    atexit.register(app.save)
    app.run()