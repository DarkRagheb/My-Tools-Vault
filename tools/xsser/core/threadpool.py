#!/usr/bin/env python
# -*- coding: utf-8 -*-"
# vim: set expandtab tabstop=4 shiftwidth=4:
"""
This file is part of the XSSer project, https://xsser.03c8.net

Copyright (c) 2010/2026 | psy <epsylon@riseup.net>

xsser is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

xsser is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with xsser; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
__docformat__ = "restructuredtext en"

__all__ = [
    'makeRequests',
    'NoResultsPending',
    'NoWorkersAvailable',
    'ThreadPool',
    'WorkRequest',
    'WorkerThread'
]

__author__ = "Christopher Arndt"
__version__ = '1.2.7'
__revision__ = "$Revision: 416 $"
__date__ = "$Date: 2009-10-07 05:41:27 +0200 (Wed, 07 Oct 2009) $"
__license__ = "MIT license"


import sys
import threading
try:
    import queue
except ImportError:
    import queue as Queue
from queue import Empty
import traceback


class NoResultsPending(Exception):
    pass

class NoWorkersAvailable(Exception):
    pass


def _handle_thread_exception(request, exc_info):
    traceback.print_exception(*exc_info)


def makeRequests(callable_, args_list, callback=None,
        exc_callback=_handle_thread_exception):
    requests = []
    for item in args_list:
        is_crawling = False
        try:
            psy = item[3]
            is_crawling = True
        except:
            is_crawling = False

        if isinstance(item, tuple):
            requests.append(
                WorkRequest(callable_, item[0], item[1], callback=callback,
                    exc_callback=exc_callback)
            )
        else:
            if is_crawling == True:
                requests.append(
                    WorkRequest(callable_, [item], None, callback=callback,
                        exc_callback=exc_callback)
                )
            else:
                requests.append(
                    WorkRequest(callable_, item, None, callback=callback,
                        exc_callback=exc_callback)
                )
    return requests


class WorkerThread(threading.Thread):

    def __init__(self, requests_queue, results_queue, poll_timeout=5, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(1)
        self._requests_queue = requests_queue
        self._results_queue = results_queue
        self._poll_timeout = poll_timeout
        self._dismissed = threading.Event()
        self.start()

    def run(self):
        while True:
            if self._dismissed.isSet():

                break


            try:
                request = self._requests_queue.get(True, self._poll_timeout)
            except Empty:
                continue
            else:
                if self._dismissed.isSet():

                    self._requests_queue.put(request)
                    break
                try:
                    result = request.callable(*request.args, **request.kwds)
                    self._results_queue.put((request, result))
                except:
                    request.exception = True
                    self._results_queue.put((request, sys.exc_info()))

    def dismiss(self):
        self._dismissed.set()


class WorkRequest:

    def __init__(self, callable_, args=None, kwds=None, requestID=None,
            callback=None, exc_callback=_handle_thread_exception):
        if requestID is None:
            self.requestID = id(self)
        else:
            try:
                self.requestID = hash(requestID)
            except TypeError:
                raise TypeError("requestID must be hashable.")
        self.exception = False
        self.callback = callback
        self.exc_callback = exc_callback
        self.callable = callable_
        self.args = args or []
        self.kwds = kwds or {}

    def __str__(self):
        return "<WorkRequest id=%s args=%r kwargs=%r exception=%s>" % \
            (self.requestID, self.args, self.kwds, self.exception)

class ThreadPool:

    def __init__(self, num_workers, q_size=0, resq_size=0, poll_timeout=5):
        self._requests_queue = queue.Queue(q_size)
        self._results_queue = queue.Queue(resq_size)
        self.workers = []
        self.dismissedWorkers = []
        self.workRequests = {}
        self.createWorkers(num_workers, poll_timeout)

    def createWorkers(self, num_workers, poll_timeout=5):
        for i in range(num_workers):
            self.workers.append(WorkerThread(self._requests_queue,
                self._results_queue, poll_timeout=poll_timeout))

    def dismissWorkers(self, num_workers, do_join=False):
        dismiss_list = []
        for i in range(min(num_workers, len(self.workers))):
            worker = self.workers.pop()
            worker.dismiss()
            dismiss_list.append(worker)

        if do_join:
            for worker in dismiss_list:
                worker.join()
        else:
            self.dismissedWorkers.extend(dismiss_list)

    def joinAllDismissedWorkers(self):
        for worker in self.dismissedWorkers:
            worker.join()
        self.dismissedWorkers = []

    def putRequest(self, request, block=True, timeout=None):
        assert isinstance(request, WorkRequest)

        assert not getattr(request, 'exception', None)
        self._requests_queue.put(request, block, timeout)
        self.workRequests[request.requestID] = request

    def addRequest(self, do_cb, data, print_cb, exception_cb, block=True,
                   timeout=None):
        requests = makeRequests(do_cb, data, print_cb, exception_cb)
        for req in requests:
            self.putRequest(req, block, timeout)

    def poll(self, block=False):
        while True:

            if not self.workRequests:
                raise NoResultsPending

            elif block and not self.workers:
                raise NoWorkersAvailable
            try:

                request, result = self._results_queue.get(block=block)

                if request.exception and request.exc_callback:
                    request.exc_callback(request, result)

                if request.callback and not \
                       (request.exception and request.exc_callback):
                    request.callback(request, result)
                del self.workRequests[request.requestID]
            except Empty:
                break

    def wait(self):
        while 1:
            try:
                self.poll(True)
            except NoResultsPending:
                break


if __name__ == '__main__':
    import random
    import time


    def do_something(data):
        time.sleep(random.randint(1,5))
        result = round(random.random() * data, 5)

        if result > 5:
            raise RuntimeError("Something extraordinary happened!")
        return result


    def print_result(request, result):
        print(("**** Result from request #%s: %r" % (request.requestID, result)))


    def handle_exception(request, exc_info):
        if not isinstance(exc_info, tuple):

            print(request)
            print(exc_info)
            raise SystemExit
        print(("**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info)))


    data = [random.randint(1,10) for i in range(20)]

    requests = makeRequests(do_something, data, print_result, handle_exception)


    data = [((random.randint(1,10),), {}) for i in range(20)]
    requests.extend(
        makeRequests(do_something, data, print_result, handle_exception)


    )


    print("Creating thread pool with 3 worker threads.")
    main = ThreadPool(3)


    for req in requests:
        main.putRequest(req)
        print(("Work request #%s added." % req.requestID))


    i = 0
    while True:
        try:
            time.sleep(0.5)
            main.poll()
            print(("Main thread working...",))
            print(("(active worker threads: %i)" % (threading.activeCount()-1, )))
            if i == 10:
                print("**** Adding 3 more worker threads...")
                main.createWorkers(3)
            if i == 20:
                print("**** Dismissing 2 worker threads...")
                main.dismissWorkers(2)
            i += 1
        except KeyboardInterrupt:
            print("**** Interrupted!")
            break
        except NoResultsPending:
            print("**** No pending results.")
            break
    if main.dismissedWorkers:
        print("Joining all dismissed worker threads...")
        main.joinAllDismissedWorkers()
