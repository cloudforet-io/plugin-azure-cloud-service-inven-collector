import os
from spaceone.inventory.libs.utils import *
from spaceone.inventory.libs.schema.metadata.dynamic_widget import CardWidget, ChartWidget
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField, DateTimeDyField, ListDyField, \
    EnumDyField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta

current_dir = os.path.abspath(os.path.dirname(__file__))

vmscaleset_count_per_location_conf = os.path.join(current_dir, 'widget/vmscaleset_count_per_location.yaml')
vmscaleset_count_per_subscription_conf = os.path.join(current_dir, 'widget/vmscaleset_count_per_subscription.yaml')
vmscaleset_total_vm_count_conf = os.path.join(current_dir, 'widget/vmscaleset_total_vm_count.yaml')

cst_vm_scale_set = CloudServiceTypeResource()
cst_vm_scale_set.name = 'VmScaleSet'
cst_vm_scale_set.group = 'Compute'
cst_vm_scale_set.service_code = 'Microsoft.Compute/virtualMachineScaleSets'
cst_vm_scale_set.labels = ['Compute', 'Storage']
cst_vm_scale_set.is_major = True
cst_vm_scale_set.is_primary = True
cst_vm_scale_set.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/azure/azure-vm-scale-set.svg',
}

cst_vm_scale_set._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Name', 'name'),
        # TextDyField.data_source('Status', 'data.'), (x)
        TextDyField.data_source('Instances', 'data.instance_count'),
        TextDyField.data_source('Resource Group', 'data.resource_group'),
        TextDyField.data_source('Location', 'data.location'),
        TextDyField.data_source('Default', 'data.virtual_machine_scale_set_power_state.profiles.capacity.default'),
        TextDyField.data_source('Max', 'data.virtual_machine_scale_set_power_state.profiles.capacity.maximum'),
        TextDyField.data_source('Min', 'data.virtual_machine_scale_set_power_state.profiles.capacity.minimum'),
        TextDyField.data_source('Azure Spot Eviction Policy', 'data.virtual_machine_profile.eviction_policy'),
        TextDyField.data_source('Subscription', 'data.subscription_name'),

        # is_optional fields
        TextDyField.data_source('Virtual network/subnet', 'data.virtual_machine_profile.network_profile.primary_vnet', options={
            'is_optional': True
        }),
        TextDyField.data_source('Host group', 'data.host_group.id', options={
            'is_optional': True
        }),
        TextDyField.data_source('Ephemeral OS Disk',
                                'data.virtual_machine_profile.storage_profile.os_disk.diff_disk_settings.option.local', options={
            'is_optional': True
        }),
        TextDyField.data_source('Azure Spot Eviction Policy', 'data.virtual_machine_profile.eviction_policy', options={
            'is_optional': True
        }),
        TextDyField.data_source('Azure Spot Max Price', 'data.virtual_machine_profile.billing_profile.max_price', options={
            'is_optional': True
        }),
        TextDyField.data_source('Termination Notification',
                                'data.virtual_machine_profile.terminate_notification_display', options={
            'is_optional': True
        }),
        TextDyField.data_source('OverProvisioning', 'data.overprovision', options={
            'is_optional': True
        }),
        TextDyField.data_source('Proximity Placement Group', 'data.proximity_placement_group_display', options={
            'is_optional': True
        }),
        TextDyField.data_source('Automatic Repairs', 'data.automatic_repairs_policy.enabled', options={
            'is_optional': True
        }),
        TextDyField.data_source('Upgrade Policy', 'data.upgrade_policy.mode', options={
            'is_optional': True
        }),
        TextDyField.data_source('Fault Domains', 'data.platform_fault_domain_count', options={
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
    ],
    widget=[
        ChartWidget.set(**get_data_from_yaml(vmscaleset_count_per_location_conf)),
        ChartWidget.set(**get_data_from_yaml(vmscaleset_count_per_subscription_conf)),
        CardWidget.set(**get_data_from_yaml(vmscaleset_total_vm_count_conf))
    ]

)


CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_vm_scale_set}),
]
