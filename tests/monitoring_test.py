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


import libvirt

import convirt
import convirt.command
import convirt.config.environ
import convirt.connection
import convirt.events
import convirt.monitoring
import convirt.runner

from . import testlib


class MonitoringTests(testlib.RunnableTestCase):

    def tearDown(self):
        convirt.doms.clear()

    def test_domain_disappeared(self):
        evt = libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE

        delivered = []

        def _cb(*args, **kwargs):
            delivered.append(args)

        conn = convirt.connection.Connection(
            convirt.command.Repo()
        )
        with testlib.named_temp_dir() as tmp_dir:
            with testlib.global_conf(run_dir=tmp_dir):
                dom = conn.createXML(testlib.minimal_dom_xml(), 0)
                conn.domainEventRegisterAny(dom, evt, _cb, None)
                convirt.monitoring.watchdog(lambda: [])

        self.assertEquals(delivered, [(
            conn,
            dom,
            libvirt.VIR_DOMAIN_EVENT_STOPPED,
            libvirt.VIR_DOMAIN_EVENT_STOPPED_SHUTDOWN,
        )])

    def test_domain_all_present(self):
        evt = libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE

        delivered = []

        def _cb(*args, **kwargs):
            delivered.append(args)

        conn = convirt.connection.Connection(
            convirt.command.Repo()
        )
        with testlib.named_temp_dir() as tmp_dir:
            with testlib.global_conf(run_dir=tmp_dir):
                dom = conn.createXML(testlib.minimal_dom_xml(), 0)
                conn.domainEventRegisterAny(dom, evt, _cb, None)

                def _fake_get_all():
                    return [dom.runtimeUUIDString()]

                convirt.monitoring.watchdog(_fake_get_all)

        self.assertEquals(delivered, [])


def _handler(*args, **kwargs):
    pass
