"""
Data feeders for Apiritif.

Copyright 2018 BlazeMeter Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import threading

import unicodecsv as csv
from itertools import cycle, islice

import apiritif.thread as thread


thread_data = threading.local()


class CSVReader(object):
    def __init__(self, filename):
        self.step = thread.get_total()
        self.first = thread.get_index()
        self.csv = {}
        self.fds = open(filename, 'rb')
        self._reader = cycle(csv.DictReader(self.fds, encoding='utf-8'))

    def close(self):
        if self.fds is not None:
            self.fds.close()
        self._reader = None

    def read_vars(self):
        if not self._reader:
            return      # todo: exception?

        if not self.csv:    # first element
            self.csv = next(islice(self._reader, self.first, self.first + 1))
        else:               # next one
            self.csv = next(islice(self._reader, self.step - 1, self.step))


class ThreadCSVReader(object):
    def __init__(self, filename):
        self.filename = filename

    def get_csv_reader(self, create=True):
        csv_readers = getattr(thread_data, "csv_readers", None)
        if not csv_readers:
            thread_data.csv_readers = {}

        csv_reader = thread_data.csv_readers.get(id(self))
        if not csv_reader and create:
            csv_reader = CSVReader(self.filename)
            thread_data.csv_readers[id(self)] = csv_reader

        return csv_reader

    def read_vars(self):
        self.get_csv_reader().read_vars()

    def close(self):
        csv_reader = self.get_csv_reader(create=False)
        if csv_reader:
            del thread_data.csv_readers[id(self)]
            csv_reader.close()

    def get_vars(self):
        csv_reader = self.get_csv_reader(create=False)
        if csv_reader:
            return csv_reader.csv
        else:
            return {}
