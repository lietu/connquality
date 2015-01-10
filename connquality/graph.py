"""
Graphing system
"""

import sys
import argparse
import dateutil.parser
import time
import numpy
import logging

import matplotlib.pyplot as pyplot
import matplotlib.dates
from matplotlib.dates import DateFormatter

from connquality.monitor import Monitor


class Reader(object):
    STATUSES = {
        Monitor.STATUS_OK: 0,
        Monitor.STATUS_DEGRADED: 0.5,
        Monitor.STATUS_ERROR: 1
    }

    def __init__(self):
        self.timestamps = None
        self.timestamp_dts = None
        self.latencies = None
        self.statuses = None
        self.lines = None
        self.entries = None

    def _iso8601_to_time(self, timestamp):
        ts_dt = dateutil.parser.parse(timestamp)
        return time.mktime(ts_dt.timetuple()) + ts_dt.microsecond / 1E6


    def _iso8601_to_datetime(self, timestamp):
        return dateutil.parser.parse(timestamp)

    def _filter(self, items, target_length):
        if len(items) < target_length:
            return items

        xth = float(len(items)) / float(target_length)
        filtered = []

        index = 0
        next_index = 0.0

        avg_ok = False
        values = []

        for item in items:
            if index == 0:
                if isinstance(item, int) or isinstance(item, float):
                    avg_ok = True

            if index >= next_index:
                if avg_ok:
                    values.append(item)
                    filtered.append(float(sum(values)) / float(len(values)))
                else:
                    filtered.append(item)
                next_index += xth
                values = []
            elif avg_ok:
                values.append(item)

            index += 1

        return filtered

    def read(self, filename, start=None, end=None, data_points=None):

        timestamps = []
        timestamp_dts = []
        latencies = []
        statuses = []

        lines = 0
        entries = 0

        if start:
            start = self._iso8601_to_time(start)
        if end:
            end = self._iso8601_to_time(start)

        with open(filename) as f:
            for line in f:
                lines += 1

                timestamp, latency, status = line[:-1].split("\t")

                parsed_timestamp = self._iso8601_to_time(timestamp)

                if start and parsed_timestamp < start:
                    continue

                if end and parsed_timestamp > end:
                    break

                entries += 1

                timestamp_dts.append(self._iso8601_to_datetime(timestamp))
                timestamps.append(parsed_timestamp)
                latencies.append(float(latency))
                statuses.append(self.__class__.STATUSES[status])

        if data_points:
            timestamps = self._filter(timestamps, data_points)
            timestamp_dts = self._filter(timestamp_dts, data_points)
            latencies = self._filter(latencies, data_points)
            statuses = self._filter(statuses, data_points)

        self.timestamps = numpy.array(timestamps)
        self.timestamp_dts = timestamp_dts
        self.latencies = numpy.array(latencies)
        self.statuses = numpy.array(statuses)

        self.lines = lines
        self.entries = entries


class Graph(object):
    def __init__(self, options):
        self.options = options
        self.logger = None

    def _initialize(self):
        """
        Initialize all the things
        """

        self.logger = logging.getLogger("connquality")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)8s] %(message)s')
        )

        self.logger.addHandler(handler)

    def _draw_graph(self, reader):
        self.logger.debug("Generating a graph")

        # Calculate figure size in inches to get correct output resolution
        dpi = float(self.options.dpi)

        pyplot.figure(dpi=dpi)
        fig, (latency_axis, status_axis) = pyplot.subplots(
            2, sharex=True, sharey=False
        )

        # Convert datetimes to matplotlib compatible data
        times = matplotlib.dates.date2num(reader.timestamp_dts)

        # Draw the plots
        latency_axis.plot_date(
            times,
            reader.latencies,
            '-'
        )

        status_axis.plot_date(
            times,
            reader.statuses,
            'r-'
        )

        # Set connection status labels
        labels = [
            label[0] + label[1:].lower()
            for label in Reader.STATUSES.keys()
        ]

        status_axis.get_yaxis().set_ticks(Reader.STATUSES.values())
        status_axis.get_yaxis().set_ticklabels(labels)

        # Format X axis dates
        latency_axis.xaxis.set_major_formatter(
            DateFormatter('%Y-%m-%d %H:%M:%S')
        )
        fig.autofmt_xdate(rotation="vertical", ha="center")

        # Final adjustments
        latency_axis.grid(True)
        pyplot.subplots_adjust(
            hspace=0.15, left=0.15, right=0.95, top=0.90, bottom=0.4
        )

        # Save to file
        self.logger.debug("Writing {0}".format(
            self.options.outfile
        ))

        pyplot.savefig(self.options.outfile, dpi=dpi)

    def run(self):
        self._initialize()

        self.logger.info("Reading {0}".format(self.options.logfile))

        if self.options.start:
            self.logger.info("Skipping entries until {0}".format(
                self.options.start
            ))

        if self.options.end:
            self.logger.info("Skipping entries after {0}".format(
                self.options.end
            ))

        if self.options.datapoints:
            self.logger.info("Only including {0} data points".format(
                self.options.datapoints
            ))

        reader = Reader()
        reader.read(self.options.logfile, self.options.start, self.options.end,
                    self.options.datapoints)

        self.logger.debug("Read {0} entries on {1} lines".format(
            reader.entries, reader.lines
        ))

        self._draw_graph(reader)


def parse_options(args):
    """
    Parse commandline arguments into options for Graph
    :param args:
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--logfile", default="connection.log",
                        help="Where is the connection quality data stored")
    parser.add_argument("--outfile", default="graph.png",
                        help="Where to store the generated graph")
    parser.add_argument("--dpi", default=100.0,
                        help="Target DPI for graph")
    parser.add_argument("--datapoints", default=None,
                        help="Limit number of datapoints to show")
    parser.add_argument("--start", default=None,
                        help="Only include entries starting from this datetime")
    parser.add_argument("--end", default=None,
                        help="Only include entries until this datetime")

    return parser.parse_args(args)


def start_grapher():
    """
    Start the graphing application
    """

    options = parse_options(sys.argv[1:])
    graph = Graph(options)
    graph.run()
