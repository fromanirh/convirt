#
# Copyright 2015-2016 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
from __future__ import absolute_import

import collections
import logging
import threading


Callback = collections.namedtuple('Callback', ['body', 'args'])


def _null_cb(*args, **kwargs):
    pass


_NULL = Callback(_null_cb, tuple())


class Handler(object):

    _log = logging.getLogger('convirt.event')

    _null = [_NULL]

    def __init__(self, name=None, parent=None):
        self._name = id(self) if name is None else name
        self._parent = parent
        self._lock = threading.Lock()
        self.events = collections.defaultdict(list)

    def register(self, event_id, cb, opaque):
        with self._lock:
            self.events[event_id].append(Callback(cb, opaque))

    def fire(self, event_id, *args):
        for cb in self.get_callbacks(event_id):
            arguments = args if cb.args is None else tuple(args + cb.args)
            return cb.body(*arguments)

    def get_callbacks(self, event_id):
        with self._lock:
            callback = self.events.get(event_id, None)
        if callback is not None:
            return callback
        if self._parent is not None:
            self._log.warning('[%s] unknown event %r',
                              self._name, event_id)
            return self._parent.get_callbacks(event_id)
        # TODO: debug?
        self._log.warning('[%s] unhandled event %r', self._name, event_id)
        return self._null

    @property
    def registered(self):
        with self._lock:
            return tuple(self.events.keys())

    # for testing purposes
    def clear(self):
        with self._lock:
            self.events.clear()


root = Handler(name='root')


def fire(event_id, *args):
    global root
    root.fire(event_id, *args)
