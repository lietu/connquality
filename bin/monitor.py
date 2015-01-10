import os
import sys


if __name__ == "__main__":
    parent = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.pardir
    ))

    sys.path.append(parent)

    from connquality.monitor import start_monitor

    start_monitor()
