#!/usr/bin/env python3
import time
from collections import OrderedDict


class Timing:
    """
    Class to measure timing for a specific task.

    Parameters
    ----------
    tag : str
        The tag or label for the timing measurement.

    Attributes
    ----------
    tag : str
        The label for the timing measurement.
    t_start : float or None
        The start time of the timing measurement.
    t_end : float or None
        The end time of the timing measurement.
    t_delta : float or None
        The time difference between the start and end times.
    total_runtime : float
        The accumulated total runtime for multiple measurements.
    call_count : int
        The number of times the timing has been measured.
    level : int
        The level of importance (hierarchy) for the timing measurement.

    Methods
    -------
    start()
        Start the timing measurement.
    stop()
        Stop the timing measurement and calculate the time difference.
    __enter__()
        Enter the context for the timing measurement.
    __exit__(exc_type, exc_val, exc_tb)
        Exit the context for the timing measurement.
    __str__()
        Return a string representation of the timing measurement.

    Examples
    --------
    # Example 1: Timing a code block using 'with' statement
    >>> with Timing('test') as t:
    ...     # Code to be timed
    ...     time.sleep(1)
    ...
    >>> print(t)
    test (s): 1.000

    # Example 2: Manually timing a code block without 'with' statement
    >>> t = Timing('test')
    >>> t.start()
    >>> # Code to be timed
    >>> time.sleep(1)
    >>> t.stop()
    >>> print(t)
    test (s): 1.000

    # Example 3: Accumulating multiple timing measurements
    >>> t = Timing('test')
    >>> t.start()
    >>> # Code to be timed
    >>> time.sleep(1)
    >>> t.stop()
    >>> t.start()
    >>> # Code to be timed again
    >>> time.sleep(0.5)
    >>> t.stop()
    >>> print(t)
    test (s): 1.500
    """

    def __init__(self, tag, level=0):
        self.tag = tag
        self.t_start = None
        self.t_end = None
        self.t_delta = None
        self.total_runtime = 0.0
        self.call_count = 0
        self.level = level

    def start(self):
        self.t_start = time.perf_counter()

    def stop(self):
        self.t_end = time.perf_counter()
        self.t_delta = self.t_end - self.t_start
        self.total_runtime += self.t_delta
        self.call_count += 1

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def __str__(self):

        tag_text = self.tag
        lev = self.level

        width = 30
        lmax = 4

        if lev > 0:
            prefix = f'{chr(0x25B7)}'
            indent = ' ' * 3 * (lmax - lev)
            ndash = width - len(indent + prefix + tag_text)
            dashes = '-' * ndash
            tag_text = f'{indent}{prefix}{dashes}{tag_text}'

        output = f'{tag_text:>{width}}  {self.total_runtime:<12.3f} {self.call_count:<10}'

        return output


class TimingGroup:
    """
    Class to group and manage multiple timing measurements.

    Attributes
    ----------
    timings : OrderedDict
        A dictionary of tag-timing pairs.

    Methods
    -------
    add(tag, level=0)
        Add a new timing measurement with the given tag.
    sort()
        Sort the timings based on the total runtime.

    Examples
    --------
    >>> timing_group = TimingGroup()
    >>>
    >>> with timing_group.add('SVD') as t_svd:
    ...     # Code to be timed for SVD
    ...     time.sleep(1)
    ...
    >>> with timing_group.add('DIAGO') as t_diago:
    ...     # Code to be timed for DIAGO
    ...     time.sleep(2)
    ...
    >>> print(t_svd)
        SVD (s): Total Runtime: 1.000, Call Count: 1
    >>>
    >>> timing_group.print_timings()
        SVD    (s): Total Runtime: 1.000, Call Count: 1
        DIAGO  (s): Total Runtime: 2.000, Call Count: 1
    """
    def __init__(self, name=None):
        # self.timings = {}
        self.name = name
        self.timings = OrderedDict()

    def add(self, tag, level=0):
        """
        Add timing to existing tag or create a new one.
        """
        if tag in self.timings:
            timing = self.timings[tag]
        else:
            timing = Timing(tag, level)
            self.timings[tag] = timing

        return timing

    def sort(self):
        self.timings = dict(sorted(self.timings.items(), key=lambda x: x[1].total_runtime, reverse=True))

    def __str__(self):

        # self.sort()
        width = 60

        output = ''
        output += f"{'=' * width}\n"

        line = f"{'=' * 20} {'Timing Summary'.upper()}"
        if self.name is None:
            end = f' {"=" * (width - len(line) - 1)}'
        else:
            end = f': {self.name} {"=" * (width - len(line) - 3 - len(self.name))}'

        output += f'{line}{end}\n'
        output += f"{'=' * width}\n"
        output += f'{"Tag":>30}  {"Time (s)":<12} {"Calls":<10}\n'
        output += f"{'-' * width}\n"

        for tag, timing_obj in self.timings.items():
            output += f'{timing_obj}\n'

        output += f"{'=' * width}\n\n"

        return output

    def to_dict(self):
        """
        Return a dictionary of timings.

        Returns
        -------
        dict
            A dictionary containing the tag-timing pairs.

        """

        timings_dict = {tag:
                            {'runtime': round(timing.total_runtime, 3), 'call_count': timing.call_count}
                            for tag, timing in self.timings.items()
                        }

        # timings_dict = {tag: timing.total_runtime for tag, timing in self.timings.items()}
        return timings_dict


def measure_runtime_and_calls(method):
    """
    Decorator function to measure the runtime and calls of a method.
    """

    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'timings'):
            # Create TimingGroup instance as an attribute
            self.timings = TimingGroup()
        timings = self.timings
        with timings.add(method.__name__, level=1) as t:
            result = method(self, *args, **kwargs)
        return result
    return wrapper
