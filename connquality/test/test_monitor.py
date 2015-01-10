"""
Tests for connquality.monitor module
"""

import unittest2
import socket
from mock import Mock
from connquality.monitor import parse_options, get_clock, TCPCheck


class TestGetClock(unittest2.TestCase):
    """
    Tests for get_clock
    """

    def test_get_clock(self):
        """
        Test that get_clock can be used for precise timing
        """

        first = get_clock()
        second = get_clock()

        elapsed = second - first

        self.assertIsInstance(elapsed, float)
        self.assertGreater(elapsed, 0)
        self.assertLess(elapsed, 0.001)


class TestTCPCheck(unittest2.TestCase):
    """
    Tests for TCPCheck
    """

    def test_initialization(self):
        """
        Test that initialization seems to work
        """

        tcp = TCPCheck("google.com:80")

        self.assertEqual(tcp.address, "google.com")
        self.assertEqual(tcp.port, 80)

    def test_invalid_address(self):
        """
        Test that invalid addresses will not be accepted
        """

        with self.assertRaises(ValueError):
            TCPCheck("")

        with self.assertRaises(ValueError):
            TCPCheck("abc:")

        with self.assertRaises(ValueError):
            TCPCheck("ab:ab")

        with self.assertRaises(ValueError):
            TCPCheck(":80")

        with self.assertRaises(ValueError):
            TCPCheck(":")

    def test_check_ok(self):
        """
        Test an OK check works
        """

        tcp = TCPCheck("example.com:1000000")

        totally_a_socket = "I AM TOTALLY A SOCKET"

        tcp._get_socket = Mock(return_value=totally_a_socket)
        tcp._close_socket = Mock()
        tcp._connect = Mock()

        elapsed = tcp.check()
        self.assertIsInstance(elapsed, float)
        self.assertGreater(elapsed, 0.0)
        self.assertLess(elapsed, 0.001)

        tcp._connect.assert_called_with(totally_a_socket)
        tcp._close_socket.assert_called_with(totally_a_socket)

    def test_check_bad(self):
        """
        Test that a failed check is detected
        """

        tcp = TCPCheck("example.com:1000000")

        totally_a_socket = "I AM TOTALLY A SOCKET"

        tcp._get_socket = Mock(return_value=totally_a_socket)
        tcp._close_socket = Mock()
        tcp._connect = Mock(side_effect=socket.error)

        elapsed = tcp.check()
        self.assertEqual(elapsed, None)

        tcp._connect.assert_called_with(totally_a_socket)


class TestParseOptions(unittest2.TestCase):
    """
    Tests for parse_options
    """

    def test_no_options(self):
        """
        Test that no options is an error
        """

        with self.assertRaises(SystemExit):
            parse_options([])

    def test_tcp(self):
        """
        Test --tcp
        """

        expected = {
            "logfile": "connection.log",
            "quiet": False,
            "tcp": [
                "google.com:80",
                "example.com:123"
            ],
            "interval": 30.0,
            "timeout": 3.0
        }

        args = "--tcp=google.com:80 --tcp=example.com:123"
        options = vars(parse_options(args.split(" ")))

        self.assertEqual(options, expected)

    def test_quiet(self):
        """
        Test that --quiet works
        """
        expected = {
            "logfile": "connection.log",
            "quiet": True,
            "tcp": ["example.com:123"],
            "interval": 30.0,
            "timeout": 3.0
        }

        args = "--tcp=example.com:123 --quiet"
        options = vars(parse_options(args.split(" ")))

        self.assertEqual(options, expected)

    def test_logfile(self):
        """
        Test --logfile
        """

        expected = {
            "logfile": "test.log",
            "quiet": False,
            "tcp": ["example.com:123"],
            "interval": 30.0,
            "timeout": 3.0
        }

        args = "--tcp=example.com:123 --logfile=test.log"
        options = vars(parse_options(args.split(" ")))

        self.assertEqual(options, expected)

    def test_interval(self):
        """
        Test --interval
        """

        expected = {
            "logfile": "connection.log",
            "quiet": False,
            "tcp": ["example.com:123"],
            "interval": 1.0,
            "timeout": 3.0
        }

        args = "--tcp=example.com:123 --interval=1"
        options = vars(parse_options(args.split(" ")))

        self.assertEqual(options, expected)

    def test_timeout(self):
        """
        Test --timeout
        """

        expected = {
            "logfile": "connection.log",
            "quiet": False,
            "tcp": ["example.com:123"],
            "interval": 30.0,
            "timeout": 0.1
        }

        args = "--tcp=example.com:123 --timeout=0.1"
        options = vars(parse_options(args.split(" ")))

        self.assertEqual(options, expected)
