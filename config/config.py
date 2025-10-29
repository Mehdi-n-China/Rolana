
from typing import Callable, Any
from functools import wraps

FLAGS = {
    "IS_GOD": False
}

def requires_flag(*flags: str) -> Callable[..., Any]:
    """Decorator to check global node flags before executing the function."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            if FLAGS.get("IS_GOD", False):
                return func(*args, **kwargs)
            for flag in flags:
                if not FLAGS.get(flag, False):
                    raise PermissionError(f"Permission Required: {flag}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class NetworkManager:
    @requires_flag("can_override")
    def manual_override(self):
        print("Doing a manual override!")


def main() -> None:
    n = NetworkManager()

    n.manual_override()

if __name__ == "__main__":
    main()
