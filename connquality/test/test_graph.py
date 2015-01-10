"""
Tests for connquality.graph module
"""

import unittest2
from mock import Mock
from connquality.graph import Reader


class TestReader(unittest2.TestCase):
    """
    Tests for Reader
    """

    def test_iso8601_to_time(self):
        """
        Test that test_iso8601_to_time produces expected results
        """

        text = '2015-01-10T21:55:36.959123'
        expected = 1420919736.959123

        reader = Reader()
        result = reader._iso8601_to_time(text)

        self.assertEqual(result, expected)

    def test_iso8601_to_datetime(self):
        """
        Test that _iso8601_to_datetime produces expected results
        """

        text = '2015-01-10T21:55:36.959123'

        reader = Reader()
        result = reader._iso8601_to_datetime(text).isoformat()

        self.assertEqual(result, text)

    def test_filter(self):
        """
        Test that _filter works ok
        """

        reader = Reader()

        source = range(1, 100)

        for i in source:
            result = reader._filter(source, i)
            self.assertEqual(len(result), i)

    def test_filter_avg(self):
        """
        Test that _filter works ok
        """

        reader = Reader()

        source = [0, 0.5, 1]
        expected = [0, 0.75]

        result = reader._filter(source, 2)

        self.assertEqual(result, expected)

        source = ["a", "b", "c"]
        expected = ["a"]

        result = reader._filter(source, 1)

        self.assertEqual(result, expected)
