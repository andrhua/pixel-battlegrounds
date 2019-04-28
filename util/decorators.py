from threading import Thread


def threaded(fun):
    def wrapper_thread(*args, **kwargs):
        t = Thread(target=fun, args=args, kwargs=kwargs)
        t.start()
    return wrapper_thread
