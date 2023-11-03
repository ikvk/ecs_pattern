import time


def timer(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        print(str(func).split(' ')[1], time.time() - t1)
        return res

    return wrapper
