try:
    from .agent import Manus
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    sys.exit(1)