import threading


class AsyncTask:
    def __init__(self, runnable, *args):
        self.runnable = runnable
        self.thread = threading.Thread(target=runnable, args=args)

    def execute(self):
        self.thread.start()

    def is_running(self):
        return self.thread.is_alive()

