from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.snapshot.data import Snapshot
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField, ListDyField, SizeField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout, \
    ListDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta

'''
SNAPSHOT
'''
# TAB - Default
snapshot_info_meta = ItemDynamicLayout.set_fields('Snapshots', fields=[

    TextDyField.data_source('Name', 'data.name'),
    TextDyField.data_source('Storage Type', 'data.sku.name'),
    SizeField.data_source('Size', 'data.size'),
    TextDyField.data_source('Source Disk', 'data.source_disk_name'),
    TextDyField.data_source('Location', 'data.location'),
    TextDyField.data_source('Resource ID', 'data.id'),
    TextDyField.data_source('Resource Group', 'data.resource_group'),
    EnumDyField.data_source('Snapshot state', 'data.disk_state', default_state={
        'safe': ['ActiveSAS', 'ActiveUpload', 'Attached', 'Reserved'],
        'warning': ['ReadyToUpload'],
        'available': ['Unattached']
    }),
    TextDyField.data_source('Snapshot Type', 'data.incremental_display'),
    TextDyField.data_source('Subscription ID', 'data.subscription_id'),
    TextDyField.data_source('Subscription Name', 'data.subscription_name'),
    TextDyField.data_source('Encryption Type', 'data.encryption.type_display'),
    TextDyField.data_source('Network Access Policy', 'data.network_access_policy_display'),
    DateTimeDyField.data_source('Created Time', 'data.time_created')
])

# TAB - tags
snapshot_info_tags = TableDynamicLayout.set_fields('Tags', 'data.tags', fields=[
    TextDyField.data_source('Key', 'key'),
    TextDyField.data_source('Value', 'value')
])

snapshot_meta = CloudServiceMeta.set_layouts([snapshot_info_meta, snapshot_info_tags])


class ComputeResource(CloudServiceResource):
    cloud_service_group = StringType(default='Compute')


class SnapshotResource(ComputeResource):
    cloud_service_type = StringType(default='Snapshot')
    data = ModelType(Snapshot)
    _metadata = ModelType(CloudServiceMeta, default=snapshot_meta, serialized_name='metadata')
    name = StringType()


class SnapshotResponse(CloudServiceResponse):
    resource = PolyModelType(SnapshotResource)
