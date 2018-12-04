import functools

def logging(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print('LOG: Running job "%s"' % function.__name__)
        result = function(*args, **kwargs)
        print('LOG: Job "%s" completed' % function.__name__)
        return result

    return wrapper