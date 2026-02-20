import logging
import functools
import inspect
import time


def trace(fn):
    """
    Decorator that logs function entry, arguments, return value and execution time.
    Only active when logger level is DEBUG.
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"{fn.__module__}.{fn.__qualname__}")

        if not logger.isEnabledFor(logging.DEBUG):
            return fn(*args, **kwargs)

        signature = inspect.signature(fn)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        args_repr = {
            k: repr(v)
            for k, v in bound.arguments.items()
        }

        start = time.perf_counter()

        logger.debug(
            "ENTER",
            extra={
                "function": fn.__qualname__,
                "call_args": args_repr,
            },
        )

        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            duration = round((time.perf_counter() - start) * 1000, 3)

            logger.debug(
                "EXCEPTION",
                extra={
                    "function": fn.__qualname__,
                    "duration_ms": duration,
                    "error": repr(e),
                },
            )
            raise

        duration = round((time.perf_counter() - start) * 1000, 3)

        logger.debug(
            "EXIT",
            extra={
                "function": fn.__qualname__,
                "duration_ms": duration,
                "result": repr(result),
            },
        )

        return result

    return wrapper