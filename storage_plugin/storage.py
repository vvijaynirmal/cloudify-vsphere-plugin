#########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from cloudify import ctx
from cloudify.decorators import operation
from cloudify import exceptions as cfy_exc
from server_plugin.server import VSPHERE_SERVER_ID
from vsphere_plugin_common import (with_storage_client,
                                   transform_resource_name,
                                   remove_runtime_properties)
from vsphere_plugin_common.constants import (
    VSPHERE_STORAGE_FILE_NAME,
    VSPHERE_STORAGE_VM_ID,
    VSPHERE_STORAGE_SCSI_ID,
    VSPHERE_STORAGE_RUNTIME_PROPERTIES,
)


@operation
@with_storage_client
def create(storage_client, **kwargs):
    ctx.logger.debug("Entering create storage procedure.")
    storage = {
        'name': ctx.node.id,
    }
    storage.update(ctx.node.properties['storage'])
    ctx.logger.info('Creating new volume with name \'{name}\' and size: {size}'
                    .format(name=storage['name'],
                            size=storage['storage_size']))
    transform_resource_name(storage, ctx)
    ctx.logger.info("Storage info: \n%s." %
                    "".join("%s: %s" % item
                            for item in storage.items()))
    storage_size = storage['storage_size']
    capabilities = ctx.capabilities.get_all().values()
    if not capabilities:
        raise cfy_exc.NonRecoverableError(
            'Error during trying to create storage: storage should be '
            'related to a VM, but capabilities are empty.')

    connected_vms = [rt_properties for rt_properties in capabilities
                     if VSPHERE_SERVER_ID in rt_properties]
    if len(connected_vms) > 1:
        raise cfy_exc.NonRecoverableError(
            'Error during trying to create storage: storage may be '
            'connected to at most one VM')

    vm_id = connected_vms[0][VSPHERE_SERVER_ID]
    ctx.logger.info('Connected storage {storage_name} to vm {vm_name}'
                    .format(storage_name=storage['name'],
                            vm_name=connected_vms[0][VSPHERE_SERVER_ID]))
    storage_file_name = storage_client.create_storage(vm_id, storage_size)

    ctx.instance.runtime_properties[VSPHERE_STORAGE_FILE_NAME] = \
        storage_file_name
    ctx.instance.runtime_properties[VSPHERE_STORAGE_VM_ID] = vm_id
    ctx.logger.info("Storage create with name %s." % storage_file_name)


@operation
@with_storage_client
def delete(storage_client, **kwargs):
    vm_id = ctx.instance.runtime_properties[VSPHERE_STORAGE_VM_ID]
    storage_file_name = \
        ctx.instance.runtime_properties[VSPHERE_STORAGE_FILE_NAME]
    storage_client.delete_storage(vm_id, storage_file_name)
    remove_runtime_properties(VSPHERE_STORAGE_RUNTIME_PROPERTIES, ctx)


@operation
@with_storage_client
def resize(storage_client, **kwargs):
    vm_id = ctx.instance.runtime_properties[VSPHERE_STORAGE_VM_ID]
    storage_file_name = \
        ctx.instance.runtime_properties[VSPHERE_STORAGE_FILE_NAME]
    storage_size = ctx.instance.runtime_properties.get('storage_size')
    if not storage_size:
        raise cfy_exc.NonRecoverableError(
            'Error during trying to resize storage: new storage size wasn\'t'
            ' specified.')
    storage_client.resize_storage(vm_id,
                                  storage_file_name,
                                  storage_size)
