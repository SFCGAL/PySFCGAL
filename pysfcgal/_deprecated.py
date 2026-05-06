from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import deprecated
else:
    try:
        # available since python 3.13
        from warnings import deprecated
    except ImportError:
        # fallback prior to python 3.13
        import functools
        import warnings

        def deprecated(message):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    warnings.warn(
                        f"{func.__name__} is deprecated: {message}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                    return func(*args, **kwargs)
                return wrapper
            return decorator
