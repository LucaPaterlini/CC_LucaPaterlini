# lambda sample
from functools import reduce

val = [1, 2, 3, 4, 5, 6]
print(reduce(lambda x, y: x * y, val, 1))


# decorators

def retry(func):
    def retried_function(*args, **kwargs):
        exc = None
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                print("Exception raised while calling %s with args:%s, kwargs: %s."
                      "Retrying" % (func, args, kwargs))
        raise exc

    return retried_function


# a decorator its an example of functional programming becouse
# it takes a function in input.

@retry
def do_something_risky():
    1 / 0


if __name__ == '__main__':
    retried_function = retry(do_something_risky)
