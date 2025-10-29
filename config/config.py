
from typing import Callable, Any
from functools import wraps

def require_authority(authority_level: int) -> Callable[..., Any]:
    """Decorator to check global node flags before executing the function."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: tuple, **kwargs: dict) -> Any:
            from flags import AUTHORITY_LEVEL
            if AUTHORITY_LEVEL < authority_level:
                raise PermissionError(f"You are not authorized to run this command. Needs: {AUTHORITY_LEVEL}, got {authority_level}.")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class NetworkManager:
    @require_authority(1)
    def manual_override(self):
        print("Doing a manual override!")


def main() -> None:
    n = NetworkManager()

    n.manual_override()

if __name__ == "__main__":
    print(__name__)
    main()
