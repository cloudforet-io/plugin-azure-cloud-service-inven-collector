import os
from spaceone.inventory.libs.utils import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, ListDyField, \
    EnumDyField, SizeField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

snapshot_count_per_location_conf = os.path.join(current_dir, 'widget/snapshot_count_per_location.yaml')
snapshot_count_per_resource_group_conf = os.path.join(current_dir, 'widget/snapshot_count_per_resource_group.yaml')
snapshot_count_per_subscription_conf = os.path.join(current_dir, 'widget/snapshot_count_per_subscription.yaml')
snapshot_total_size_conf = os.path.join(current_dir, 'widget/snapshot_total_size.yaml')


cst_snapshot = CloudServiceTypeResource()
cst_snapshot.name = 'Snapshot'
cst_snapshot.group = 'Compute'
cst_snapshot.service_code = 'Microsoft.Compute/snapshots'
cst_snapshot.labels = ['Compute', 'Storage']
cst_snapshot.is_primary = False
cst_snapshot.is_major = False
cst_snapshot.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/azure/azure-disk-snapshot.svg',
}

cst_snapshot._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'name'),
        TextDyField.data_source('Source disk', 'data.source_disk_name'),
        TextDyField.data_source('Snapshot type', 'data.incremental_display'),
        SizeField.data_source('Source disk size', 'data.disk_size_bytes'),
        TextDyField.data_source('Resource Group', 'data.resource_group'),
        TextDyField.data_source('Location', 'data.location'),
        TextDyField.data_source('Subscription', 'data.subscription_name'),
        DateTimeDyField.data_source('Time created', 'launched_at'),

        # is_optional fields - Default
        TextDyField.data_source('Subscription ID', 'account', options={
            'is_optional': True
        }),
        TextDyField.data_source('Encryption Type', 'data.encryption.type_display', options={
            'is_optional': True
        }),
        TextDyField.data_source('Network Access Policy', 'data.network_access_policy_display', options={
            'is_optional': True
        })
    ],
    search=[
        SearchField.set(name='ID', key='data.id', data_type='string'),
        SearchField.set(name='Name', key='name', data_type='string'),
        SearchField.set(name='Subscription ID', key='account', data_type='string'),
        SearchField.set(name='Subscription Name', key='data.subscription_name', data_type='string'),
        SearchField.set(name='Resource Group', key='data.resource_group', data_type='string'),
        SearchField.set(name='Location', key='data.location', data_type='string'),
        SearchField.set(name='Storage Account Type', key='instance_type', data_type='string'),
        SearchField.set(name='Snapshot Type', key='data.incremental_display', data_type='string'),
        SearchField.set(name='Disk Size (Bytes)', key='data.disk_size_bytes', data_type='integer'),
        SearchField.set(name='Disk Size (GB)', key='instance_size', data_type='float'),
        SearchField.set(name='Encryption', key='data.encryption.type_display', data_type='string'),
        SearchField.set(name='Network Access Policy', key='data.network_access_policy', data_type='string'),
        SearchField.set(name='Provisioning State', key='data.provisioning_state', data_type='string'),
        SearchField.set(name='Creation Time', key='launched_at', data_type='datetime')
    ],
    widget=[
        ChartWidget.set(**get_data_from_yaml(snapshot_count_per_location_conf)),
        ChartWidget.set(**get_data_from_yaml(snapshot_count_per_resource_group_conf)),
        ChartWidget.set(**get_data_from_yaml(snapshot_count_per_subscription_conf)),
        CardWidget.set(**get_data_from_yaml(snapshot_total_size_conf))
    ]
)


CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_snapshot}),
]
