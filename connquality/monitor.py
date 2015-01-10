"""
Monitoring system
"""

import sys
import argparse
import time
import datetime
import socket
import logging
import platform


IS_WINDOWS = platform.system() == "Windows"


def get_clock():
    """
    Get a timestamp with high resolution for calculating elapsed time

    :return: A timestamp (not necessarily a unix timestamp)
    :rtype: float
    """
    if IS_WINDOWS:
        return time.clock()
    else:
        return time.time()


class Check(object):
    """
    Base class for all connection checks
    """

    def __init__(self, destination, logger=None):
        self.destination = destination
        self.logger = logger
        self.parse_destination(destination)

    def parse_destination(self, destination):
        """
        Validate and parse destination address
        """

        raise NotImplementedError(
            "Class {0} doesn't implement set_destination()".format(
                self.__class__.__name__
            )
        )

    def check(self):
        """
        Run the connection check

        :returns: Latency in seconds or None if failed
        """

        raise NotImplementedError("Class {0} doesn't implement check()".format(
            self.__class__.__name__
        ))


class TCPCheck(Check):
    """
    TCP/IP connection check
    """

    def __init__(self, destination, logger=None):
        self.address = None
        self.port = None

        super(TCPCheck, self).__init__(destination, logger)

    def parse_destination(self, destination):
        if ":" not in destination:
            raise ValueError("TCP address {0} doesn't look valid "
                             "(no : found)".format(destination))

        address, port = destination.split(":")

        if not address:
            raise ValueError("TCP address {0} doesn't look valid "
                             "(no address specified)".format(destination))

        if not port:
            raise ValueError("TCP address {0} doesn't look valid "
                             "(no port specified)".format(destination))

        try:
            port = int(port)
        except ValueError:
            raise ValueError("TCP address {0} doesn't look valid "
                             "(port is not a number)".format(destination))

        self.address = address
        self.port = port

    def check(self):
        if self.logger:
            self.logger.debug("Checking connection to {0}".format(
                self.destination
            ))

        try:
            soc = self._get_socket()

            start = get_clock()
            self._connect(soc)
            end = get_clock()

            self._close_socket(soc)

            elapsed = round(end - start, 6)

            if self.logger:
                self.logger.debug(
                    "Connection to {0} established in {1}s".format(
                        self.destination, elapsed
                    )
                )

            return elapsed
        except socket.error as err:
            if self.logger:
                self.logger.warn("Caught socket error when connecting to "
                                 "{0}".format(self.destination))
                self.logger.warn(err)

            return None

    def _get_socket(self):
        """
        Return a new socket, overridden in tests
        """

        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _close_socket(self, soc):
        """
        Close the given socket, overridden in tests
        """

        soc.close()

    def _connect(self, soc):
        """
        Connect to the address with the given socket, overridden in tests
        """

        soc.connect((self.address, self.port))


class Monitor(object):
    """
    Manages connection monitoring and logging
    """

    STATUS_ERROR = "ERROR"
    STATUS_DEGRADED = "DEGRADED"
    STATUS_OK = "OK"

    def __init__(self, options):
        self.options = options
        self.logger = None
        self.checks = []

    def _initialize(self):
        """
        Initialize all the things
        """
        self._initialize_logger()

        socket.setdefaulttimeout(self.options.timeout)

        for tcp_address in self.options.tcp:
            self.checks.append(TCPCheck(tcp_address, self.logger))

    def _initialize_logger(self):
        """
        Set up a console logger
        """

        self.logger = logging.getLogger("connquality")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        if self.options.quiet:
            handler.setLevel(logging.ERROR)
        else:
            handler.setLevel(logging.DEBUG)

        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)8s] %(message)s')
        )

        self.logger.addHandler(handler)

    def _run_checks(self):
        """
        Runs all the checks, determines average latency and connection status

        :return: avg latency, Monitor.STATUS_*
        """

        if self.logger:
            self.logger.debug("Running checks")

        check_count = len(self.checks)
        errors = 0
        latencies = []

        for check in self.checks:
            latency = check.check()

            if latency is None:
                errors += 1
            else:
                latencies.append(latency)

        if errors == check_count:
            if self.logger:
                self.logger.debug("All checks failed")
            result = self.STATUS_ERROR
        elif errors > 0:
            if self.logger:
                self.logger.debug("Some checks failed")
            result = self.STATUS_DEGRADED
        else:
            if self.logger:
                self.logger.debug("All tests OK")
            result = self.STATUS_OK

        if latencies:
            avg_latency = round(sum(latencies) / float(check_count), 6)
        else:
            avg_latency = self.options.timeout

        if self.logger:
            self.logger.info("Average latency {0}s".format(avg_latency))

        return avg_latency, result

    def _get_timestamp(self, timestamp=None):
        """
        Get the current time in a standard format for the log file
        :param timestamp: Optionally override current time, e.g. for tests
        :return: ISO 8601 timestamp string
        """

        if not timestamp:
            timestamp = time.time()

        timestamp_dt = datetime.datetime.fromtimestamp(timestamp)
        return timestamp_dt.isoformat()

    def _sleep(self, elapsed):
        """
        Sleep until it's time for the next iteration

        :param elapsed: Time spent in the previous iteration
        """
        remaining = round(self.options.interval - elapsed, 3)

        if self.logger:
            self.logger.debug("Waiting for {0}s before next iteration".format(
                remaining
            ))

        if remaining > 0:
            time.sleep(remaining)

    def run(self):
        """
        Run the monitor
        """

        self._initialize()

        if self.logger:
            self.logger.info("Starting connquality monitor")

        with open(self.options.logfile, 'a') as monitoring_log:
            while True:
                start = get_clock()

                latency, result = self._run_checks()
                timestamp = self._get_timestamp()

                line = "\t".join([timestamp, str(latency), result]) + "\n"
                monitoring_log.write(line)

                end = get_clock()
                self._sleep(end - start)


def parse_options(args):
    """
    Parse commandline arguments into options for Monitor
    :param args:
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tcp",
        required=True,
        action="append",
        help="TCP/IP address to monitor, e.g. google.com:80. For best results"
             " use multiple addresses."
    )
    parser.add_argument("--logfile", default="connection.log",
                        help="Where to store the connection quality data")
    parser.add_argument("--interval", default=30.0, type=float,
                        help="How many seconds between checks")
    parser.add_argument("--timeout", default=3.0, type=float,
                        help="How many seconds to wait for connection")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Do not output log data to screen")

    return parser.parse_args(args)


def start_monitor():
    """
    Start the monitoring application
    """

    options = parse_options(sys.argv[1:])
    monitor = Monitor(options)
    monitor.run()
