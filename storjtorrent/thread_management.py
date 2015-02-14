#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Josh Brandoff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from threading import Thread, Event
from time import sleep


class StoppableThread(Thread):

    """A subclass of Thread that can be safely stopped.

    Source: http://stackoverflow.com/a/5852044/1183175
    """

    def __init__(self):
        """Initialize the stoppable thread."""
        Thread.__init__(self)
        self.stop_event = Event()
        self.daemon = True

    def stop(self):
        """Stop thread if it is alive."""
        if self.isAlive():
            # Set event to signal thread to terminate.
            self.stop_event.set()
            # Block calling thread until thread really has terminated.
            self.join()


class IntervalTimer(StoppableThread):

    """A subclass of StoppableThread that runs a method at a set interval.

    Source: http://stackoverflow.com/a/22702362/1183175
    """

    def __init__(self, interval, worker_func):
        """Initialize the interval timer.

        :param interval: The interval, in seconds, with which the method should
                         be repeated.
        :type: int or float
        :param worker_func: The method or function which should be repeatedly
                            run inside the thread.
        :type worker_func: function
        """
        super(IntervalTimer, self).__init__()
        self._interval = interval
        self._worker_func = worker_func

    def run(self):
        """Run the interval timer process."""
        while not self.stop_event.is_set():
            self._worker_func()
            sleep(self._interval)
