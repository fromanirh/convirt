from __future__ import absolute_import
#
# Copyright 2016 Red Hat, Inc.
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

import collections
import logging
import os.path
import subprocess

from . import command
from . import config
from . import runner


_NULL = command.Path('false', paths=tuple())


class Unsupported(Exception):
    """
    TODO
    """


class ConfigError(Exception):
    """
    TODO
    """


# TODO: networking
RunConfig = collections.namedtuple('RunConfig',
                                   ['image_path', 'memory_size_mib'])


class Base(object):

    _log = logging.getLogger('convirt.runtime.Base')

    NAME = ''

    _PATH = _NULL

    @classmethod
    def available(cls):
        try:
            return cls._PATH.cmd() is not None
        except command.NotFound:
            return False

    def __init__(self, vm_uuid, conf=None):
        self._vm_uuid = vm_uuid
        self._conf = config.current() if conf is None else conf
        self._run_conf = None
        self._runner = runner.Runner(self.unit_name(), self._conf)

    def unit_name(self):
        return "%s%s" % (runner.PREFIX, self._vm_uuid)

    def configure(self, xml_tree):
        self._log.debug('configuring container %s', self._vm_uuid)
        mem = self._find_memory(xml_tree)
        path = self._find_image(xml_tree)
        # TODO: network
        self._run_conf = RunConfig(path, mem)
        self._log.debug('configured container %s: %s',
                        self._vm_uuid, self._run_conf)

    def start(self, target=None):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def runtime_name(self):
        raise NotImplementedError

    def setup(self):
        pass  # optional

    def teardown(self):
        pass  # optional

    @property
    def runtime_config(self):
        """
        Shortcut for test purposes only. May be removed in future versions.
        """
        return self._run_conf

    def _find_memory(self, xml_tree):
        mem_node = xml_tree.find('./maxMemory')
        if mem_node is not None:
            mem = int(mem_node.text)/1024
            self._log.debug('container %s found memory = %i MiB',
                            self._vm_uuid, mem)
            return mem
        raise ConfigError('memory')

    def _find_image(self, xml_tree):
        disks = xml_tree.findall('.//disk[@type="file"]')
        for disk in disks:
            # TODO: add in the findall() above?
            device = disk.get('device')
            if device != 'disk':
                continue
            source = disk.find('./source/[@file]')
            if source is None:
                continue
            image_path = source.get('file')
            if not image_path:
                continue
            self._log.debug('container %s found image path = [%s]',
                            self._vm_uuid, image_path)
            return image_path
        raise ConfigError('image path not found')
