# Copyright (c) 2014-2019 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from mock import Mock

from cloudify.state import current_ctx
from cloudify.exceptions import NonRecoverableError

import vsphere_plugin_common


class NetworkClientTest(unittest.TestCase):

    def setUp(self):
        super(NetworkClientTest, self).setUp()
        self.mock_ctx = Mock()
        current_ctx.set(self.mock_ctx)

    def test_delete_ippool(self):
        client = vsphere_plugin_common.NetworkClient()
        datacenter = Mock()
        client._get_obj_by_name = Mock(return_value=datacenter)
        client.si = Mock()
        # check delete code
        client.delete_ippool("datacenter", 123)
        # checks
        client._get_obj_by_name.assert_called_once_with(
            vsphere_plugin_common.vim.Datacenter, "datacenter")
        client.si.content.ipPoolManager.DestroyIpPool.assert_called_once_with(
            dc=datacenter.obj, force=True, id=123)

        # no such datacenter
        client._get_obj_by_name = Mock(return_value=None)
        with self.assertRaises(NonRecoverableError):
            client.delete_ippool("datacenter", 123)


if __name__ == '__main__':
    unittest.main()
