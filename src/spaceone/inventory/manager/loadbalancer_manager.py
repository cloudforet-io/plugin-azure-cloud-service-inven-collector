from spaceone.inventory.libs.manager import AzureManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from pprint import pprint
from spaceone.inventory.connector.loadbalncer import LoadBalancerConnector
from spaceone.inventory.model.loadbalancer.cloud_service import *
from spaceone.inventory.model.loadbalancer.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.loadbalancer.data import *
import time


class LoadBalancerManager(AzureManager):
    connector_name = 'LoadBalancerConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        print("** LoadBalancer START **")
        start_time = time.time()
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
                - subscription_info
        Response:
            CloudServiceResponse
        """
        secret_data = params['secret_data']
        subscription_info = params['subscription_info']

        load_balancer_conn: LoadBalancerConnector = self.locator.get_connector(self.connector_name, **params)
        load_balancers = []
        for load_balancer in load_balancer_conn.list_load_balancers():
            load_balancer_dict = self.convert_nested_dictionary(self, load_balancer)
            # update vm_scale_set_dict
            load_balancer_dict.update({
                'resource_group': self.get_resource_group_from_id(load_balancer_dict['id']),
                # parse resource_group from ID
                'subscription_id': subscription_info['subscription_id'],
                'subscription_name': subscription_info['subscription_name'],
            })

            # Get Network Interfaces attached in this load balancer
            load_balancer_dict.update({
                'network_interfaces': self.get_network_interfaces(self, load_balancer_conn,
                                                                  load_balancer_dict['resource_group'],
                                                                  load_balancer_dict['name'])
            })

            # Get Frontend IP Configurations information
            if load_balancer_dict.get('frontend_ip_configurations') is not None:
                private_ip_address_list = list()
                used_by_list = list()
                for fic in load_balancer_dict['frontend_ip_configurations']:
                    if fic.get(
                            'subnet'):  # If the 'public' type, Skip this part because there isn't subnet information for them.
                        fic['subnet']['address_prefix'] = self.get_frontend_address_prefix(self, load_balancer_conn,
                                                                                           fic['subnet'])
                        fic['subnet']['name'] = self.get_frontend_ip_subnet_name(fic['subnet']['id'])

                    # Get used inbound NAT rules
                    if fic.get('inbound_nat_rules') is not None:
                        load_balancer_dict.update({
                            'frontend_ip_configurations_used_by_display': self.get_frontend_ip_configurations_used_by_display(
                                used_by_list, fic['inbound_nat_rules'])
                        })

                    # Get used load balancing NAT rules
                    if fic.get('load_balancing_rules') is not None:
                        load_balancer_dict.update({
                            'frontend_ip_configurations_used_by_display': self.get_frontend_ip_configurations_used_by_display(
                                used_by_list, fic['load_balancing_rules']),
                        })

                    # Get all of private ip addresses
                    private_ip_address_list.append(fic['private_ip_address'])

                    load_balancer_dict.update({
                        'private_ip_address_display': private_ip_address_list
                    })

            # Since Azure python sdk returns only one backend pool, delete the backend pool list first, and then use the new API connection
            if load_balancer_dict.get('backend_address_pools') is not None:
                load_balancer_dict['backend_address_pools'].clear()
                load_balancer_dict.update({
                    'backend_address_pools': self.list_load_balancer_backend_address_pools(self, load_balancer_conn,
                                                                                           load_balancer_dict[
                                                                                               'resource_group'],
                                                                                           load_balancer_dict['name'],
                                                                                           load_balancer_dict[
                                                                                               'network_interfaces'])
                })
                # get backend address pool's count
                load_balancer_dict.update({
                    'backend_address_pools_count_display': self.get_backend_address_pools_count(self,
                                                                                                load_balancer_dict[
                                                                                                    'backend_address_pools'])
                })

            # Get load balancing Rules for display
            if load_balancer_dict.get('load_balancing_rules') is not None:
                load_balancer_dict.update({
                    'load_balancing_rules_display': self.get_load_balancing_rules_display(self, load_balancer_dict[
                        'load_balancing_rules']),
                })

                for lbr in load_balancer_dict['load_balancing_rules']:
                    if lbr.get('backend_address_pool') is not None:
                        lbr.update({
                            'backend_address_pool_display': self.get_backend_address_pool_name(
                                lbr['backend_address_pool']),
                        })

                    if lbr.get('load_distribution') is not None:
                        lbr.update({
                            'load_distribution_display': self.get_load_distribution_display(lbr['load_distribution'])
                        })

                    if lbr.get('frontend_ip_configuration') is not None:
                        lbr.update({
                            'frontend_ip_configuration_display': self.get_frontend_ip_configuration_display(
                                lbr['frontend_ip_configuration'])
                        })

            # Get Inbound NAT Rules for display
            if load_balancer_dict.get('inbound_nat_rules') is not None:
                load_balancer_dict.update({
                    'inbound_nat_rules_display': self.get_nat_rules_display(self,
                                                                            load_balancer_dict['inbound_nat_rules'])
                })
                for inr in load_balancer_dict['inbound_nat_rules']:
                    inr.update({
                        'frontend_ip_configuration_display': self.get_frontend_ip_configuration_display(
                            inr['frontend_ip_configuration']),
                        'port_mapping_display': self.get_port_mapping_display(inr['frontend_port'],
                                                                              inr['backend_port']),
                        'target_virtual_machine': self.get_matched_vm_info(self, inr['backend_ip_configuration']['id'],
                                                                           load_balancer_dict['network_interfaces'])
                    })

            # Get Health Probes for display
            if load_balancer_dict.get('probes') is not None:
                load_balancer_dict.update({
                    'probes_display': self.get_probe_display_list(self, load_balancer_dict['probes'])
                })

            # switch tags form
            tags = load_balancer_dict.get('tags', {})
            _tags = self.convert_tag_format(tags)
            load_balancer_dict.update({
                'tags': _tags
            })

            print(f'[LOAD BALANCER INFO] {load_balancer_dict}')

            load_balancer_data = LoadBalancer(load_balancer_dict, strict=False)
            load_balancer_resource = LoadBalancerResource({
                'data': load_balancer_data,
                'region_code': load_balancer_data.location,
                'reference': ReferenceModel(load_balancer_data.reference()),
                'tags': _tags,
                'name': load_balancer_data.name
            })

            # Must set_region_code method for region collection
            self.set_region_code(load_balancer_data['location'])
            load_balancers.append(LoadBalancerResponse({'resource': load_balancer_resource}))

        print(f'** LoadBalancer Finished {time.time() - start_time} Seconds **')
        return load_balancers

    @staticmethod
    def get_resource_group_from_id(dict_id):
        resource_group = dict_id.split('/')[4]
        print(f'RESOURCE_GROUP_NAME: {resource_group}')
        return resource_group

    @staticmethod
    def get_network_interfaces(self, load_balancer_conn, rg_name, lb_name):
        network_interface_object_list = list(load_balancer_conn.list_load_balancer_network_interfaces(rg_name, lb_name))
        network_interface_list = []  # list for return values

        # network_interfaces >> network_interfaces >> ip_configurations
        for nil in network_interface_object_list:
            network_interface_dict = self.convert_nested_dictionary(self, nil)
            print(f'[NETWORK_INTERFACE_DICT] {network_interface_dict}')
            nic_rg_name = network_interface_dict.get('id', '').split('/')[4]

            if network_interface_dict.get('ip_configurations') is not None:
                # Loop for getting LB's name, VMs name attached to Backend Pool
                for ip_configuration in network_interface_dict['ip_configurations']:
                    if ip_configuration.get('load_balancer_backend_address_pools') is not None:
                        for ic in ip_configuration['load_balancer_backend_address_pools']:
                            # Get backend address vm name
                            backend_pool_vm_name = ic['id'].split('/')[10]

                        network_interface_dict.update({
                            'load_balancer_backend_address_pools_name_display': backend_pool_vm_name,
                        })

                # Get the primary ip configuration from a network interface card
                network_interface_dict.update({
                    'private_ip_display': self.get_ip_configuration_display(network_interface_dict['ip_configurations'])
                })

            # 2) Get VM's name which is attached to this network interface card
            if network_interface_dict.get('virtual_machine') is not None:
                network_interface_dict.update({
                    'virtual_machine_name_display': network_interface_dict['virtual_machine']['id'].split('/')[8]
                })

            network_interface_list.append(network_interface_dict)

        return network_interface_list

    @staticmethod
    def get_ip_configurations_list(self, load_balancer_conn, rg_name, network_interface_name):
        print(f' network_interface_name:{network_interface_name}')
        print(f' rg_name:{rg_name}')
        ip_configuration_list = []
        ip_configurations_object_list = []
        if network_interface_name:
            try:
                ip_configurations_object = load_balancer_conn.list_network_interface_ip_configurations(rg_name, network_interface_name)
                ip_configurations_object_list = list(ip_configurations_object)

            except Exception as e:
                print(f'[ERROR: List load balancer Network IP configurations list]: {e}')

            try:
                for ip_configuration_object in ip_configurations_object_list:
                    print(f' ip_configuration_object:{ip_configuration_object}')
                    type_obj = type(ip_configuration_object)
                    print(f' ip_configuration_object_type:{type_obj}')
                    ip_object_dict = self.convert_nested_dictionary(self, ip_configuration_object)
                    ip_configuration_list.append(ip_object_dict)

            except Exception as e:
                print(f'[ERROR: list IP configuration object]: {e}')

        return ip_configuration_list

    @staticmethod
    def get_ip_configuration_display(ip_configurations_list):
        ic_list = list()
        for ic in ip_configurations_list:
            ic_list.append(ic['private_ip_address'])
        return ic_list

    @staticmethod
    def get_frontend_address_prefix(self, conn, subnet):
        # Parse Vnet, LB name from subnet id
        subnet_id = subnet['id']
        resource_group_name = subnet_id.split('/')[4]
        vnet_name = subnet_id.split('/')[8]
        subnet_name = subnet_id.split('/')[10]

        # API request for subnet dictionary
        subnet = conn.get_subnets(resource_group_name, vnet_name, subnet_name)

        return subnet.address_prefix

    @staticmethod
    def get_frontend_ip_subnet_name(subnet_id):
        subnet_name = subnet_id.split('/')[10]
        return subnet_name

    @staticmethod
    def get_frontend_ip_configurations_used_by_display(used_by_list, used_object_list):
        for used_object in used_object_list:
            used_by_list.append(used_object['id'].split('/')[10])

        return used_by_list

    @staticmethod
    def list_load_balancer_backend_address_pools(self, conn, rg_name, lb_name, network_interfaces_list):
        backend_pools_list = list()  # return result list

        backend_pools_object = conn.list_load_balancer_backend_address_pools(rg_name, lb_name)
        backend_pools_object_list = list(
            backend_pools_object)  # Since return type is ItemPagedClass, change to the list before convert dictionary

        # Loop for converting backend pools objects to dictionary
        for bp in backend_pools_object_list:
            backend_pool_dict = self.convert_nested_dictionary(self, bp)

            # Loop for getting vm's id and name linked to this backend address pool
            '''
            for bic in backend_pool_dict['backend_ip_configurations']:
                vm_id = self.get_matched_vm_info(self, bic['id'], network_interfaces_list)

            backend_pool_dict.update({
                'vm_ids': vm_id
            })
            '''
            backend_pools_list.append(backend_pool_dict)

        return backend_pools_list

    @staticmethod
    def get_backend_address_pools_count(self, backend_address_dict):
        backend_address_pools_count = len(backend_address_dict)

        if backend_address_pools_count == 1:
            backend_address_pools_count_display = str(backend_address_pools_count) + " backend pool"
        else:
            backend_address_pools_count_display = str(backend_address_pools_count) + " backend pools"

        return backend_address_pools_count_display

    @staticmethod
    def get_matched_vm_info(self, find_key, find_list_pool):
        matched_vm_list = list()
        for find_object in find_list_pool:
            if find_object['id'] in find_key:  # if network interface card's id matches to the backend configuration's id
                if find_object.get('virtual_machine') is not None:
                    matched_vm_list.append((find_object['virtual_machine']['id']).split('/')[8])
        return matched_vm_list

    @staticmethod
    def get_probe_display_list(self, probes_list):
        probe_display_list = list()
        for probe in probes_list:
            probe_display_list.append(probe['name'])
        return probe_display_list

    @staticmethod
    def get_load_balancing_rules_display(self, load_balancing_rules_list):
        lbr_name_list = list()
        for lbr in load_balancing_rules_list:
            lbr_name_list.append(lbr['name'])  # 'name' key always exists if there are load balancing rules.

        return lbr_name_list

    @staticmethod
    def get_nat_rules_display(self, inbound_nat_rules_list):
        nat_rules_list = list()
        for inr in inbound_nat_rules_list:
            nat_rules_list.append(inr['name'])  # 'name' key always exists if there are inbound NAT rules.

        return nat_rules_list

    @staticmethod
    def get_backend_address_pool_name(
            lbr_backend_address_pool):  # id must exist if there is a backend address pool object
        return lbr_backend_address_pool['id'].split('/')[10]

    @staticmethod
    def get_load_distribution_display(lbr_load_distribution):
        if lbr_load_distribution == 'Default':
            lbr_load_distribution_display = 'None'
        elif lbr_load_distribution == 'SourceIPProtocol':
            lbr_load_distribution_display = 'Client IP and Protocol'
        elif lbr_load_distribution == 'SourceIP':
            lbr_load_distribution_display = 'Client IP'

        return lbr_load_distribution_display

    @staticmethod
    def get_frontend_ip_configuration_display(lbr_frontend_ip_configuration_dict):
        return lbr_frontend_ip_configuration_dict['id'].split('/')[10]

    @staticmethod
    def get_port_mapping_display(frontend_port, backend_port):
        if frontend_port == backend_port:
            port_mapping_display = 'Default'
        else:
            port_mapping_display = 'Custom'
        return port_mapping_display
