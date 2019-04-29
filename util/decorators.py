from threading import Thread


def threaded(name):
    def decorator_threaded(fun):
        def wrapper_thread(*args, **kwargs):
            t = Thread(target=fun, args=args, kwargs=kwargs)
            t.name = name
            t.start()
        return wrapper_thread
    return decorator_threaded
