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

import xml.etree.ElementTree as ET

import convirt
import convirt.config
import convirt.config.environ
import convirt.command
import convirt.runner
import convirt.runtimes as rts

from . import testlib


class DockerTests(testlib.RunnableTestCase):

    def test_created_not_running(self):
        docker = rts.docker.Docker(
            convirt.config.environ.current(),
            convirt.command.Repo(),
        )
        self.assertFalse(docker.running)

    def test_start_stop(self):
        docker = rts.docker.Docker(
            testlib.make_conf(run_dir=self.run_dir),
            convirt.command.Repo(),
        )
        root = ET.fromstring(testlib.minimal_dom_xml())
        docker.configure(root)
        docker.start()
        try:
            self.assertTrue(docker.running)
        finally:
            docker.stop()
            self.assertFalse(docker.running)

    def test_start_twice(self):
        docker = rts.docker.Docker(
            testlib.make_conf(run_dir=self.run_dir),
            convirt.command.Repo(),
        )
        root = ET.fromstring(testlib.minimal_dom_xml())
        docker.configure(root)
        docker.start()
        try:
            self.assertRaises(convirt.runner.OperationFailed,
                              docker.start)
        finally:
            # not part of the test, but we don't want
            # to pollute the environment
            docker.stop()

    def test_stop_not_started(self):
        docker = rts.docker.Docker(
            testlib.make_conf(run_dir=self.run_dir),
            convirt.command.Repo(),
        )
        self.assertFalse(docker.running)
        self.assertRaises(convirt.runner.OperationFailed, docker.stop)
