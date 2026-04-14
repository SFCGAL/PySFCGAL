import functools

try:
    import icontract

    has_icontract = True
except ImportError:
    has_icontract = False


def cond_icontract(lambda_func, contract_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            icontract_decorator = getattr(icontract, contract_name)
            decorated_func = icontract_decorator(lambda_func)(func)
            return decorated_func(*args, **kwargs)
        if not has_icontract:
            return func
        return wrapper
    return decorator
