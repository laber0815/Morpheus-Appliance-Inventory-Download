

"""
HPE Morpheus Server Detail Gathering Module
Python version of hpe_morhpeus_gather_detail.pm
"""

import json
# Import custom modules
from lib.hpe_extract_instance_data import extract_instance_data
from lib.hpe_extract_server_data import extract_server_data
from lib.hpe_extract_cloud_data import extract_cloud_data
from lib.logger import logger

# Application version information
__version__ = "0.2.22"
__build_date__ = "06/04/2026 12:59:47"
__author__ = "Lars Berger (lars.berger@hpe.com)"

# Debug flag
DEBUG = False

def set_debug(value):
    """Set debug mode flag"""
    global DEBUG
    DEBUG = value

# Configuration for different resource types
RESOURCE_CONFIG = {
    'cloud': {
        'endpoint': '/api/zones',
        'response_key': 'zone',
        'extract_func': extract_cloud_data,
        'debug_prefix': 'cloud',
        'query_params': ''
    },
    'server': {
        'endpoint': '/api/servers',
        'response_key': 'server',
        'extract_func': extract_server_data,
        'debug_prefix': 'host',
        'query_params': ''
    },
    'instance': {
        'endpoint': '/api/instances',
        'response_key': 'instance',
        'extract_func': extract_instance_data,
        'debug_prefix': 'instance',
        'query_params': '?details=true'
    }
}

def gather_resource_details(session, base_url, resources, resource_type, verify=True):
    """
    Generic function to gather detailed information for any resource type
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        resources: List of resource objects from API
        resource_type: Type of resource ('cloud', 'server', 'instance')
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed resource data dictionaries
    """
    logger.info(f"Gathering {resource_type} details")
    if resource_type not in RESOURCE_CONFIG:
        raise ValueError(f"Unknown resource type: {resource_type}")
    
    config = RESOURCE_CONFIG[resource_type]
    results = []
    
    for resource in resources:
        if not resource.get('id'):
            continue
        
        id = resource['id']
        url = f"{base_url}{config['endpoint']}/{id}{config['query_params']}"
        
        try:
            # Make API call to get resource details
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()
            
            # Export response to file for debugging only
            if DEBUG:
                with open(f"{config['debug_prefix']}_{id}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)
                    
            if data and data.get(config['response_key']):
                # Extract data using the appropriate extraction function
                extracted_data = config['extract_func'](data)
                # All extract functions return lists, so extend results
                results.extend(extracted_data)
        except Exception as e:
            logger.error(f"Error fetching details for {resource_type} {id}: {e}")
            print(f"Error fetching details for {resource_type} {id}: {e}")
            # Add basic resource info if detailed fetch fails
            # results.append(resource)
    
    return results

def gather_cloud_details(session, base_url, clouds, verify=True):
    """
    Gather detailed information for each cloud by ID
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        clouds: List of cloud objects from API
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed cloud data dictionaries
    """
    return gather_resource_details(session, base_url, clouds, 'cloud', verify=verify)


def gather_cloud_list_details(session, base_url, verify=True):
    """
    Gather all clouds from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of cloud data dictionaries
    """
    logger.info("Gathering cloud list details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/zones?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"cloud_list_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            clouds = data.get('zones', data.get('zone', []))
            if not clouds:
                break

            results.extend(clouds)

            if len(clouds) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching clouds at offset {offset}: {e}")
            print(f"Error fetching clouds at offset {offset}: {e}")
            break

    return results

def gather_server_details(session, base_url, servers, verify=True):  
    """
    Gather detailed information for each server by UUID
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        servers: List of server objects from API
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed server data dictionaries
    """
    return gather_resource_details(session, base_url, servers, 'server', verify=verify)

def gather_instance_details(session, base_url, instances, verify=True):
    """
    Gather detailed information for each instance by ID
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        instances: List of instance objects from API
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed instance data dictionaries
    """
    return gather_resource_details(session, base_url, instances, 'instance', verify=verify)

def gather_group_details(session, base_url, verify=True):
    """
    Gather all groups from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of group data dictionaries
    """
    logger.info("Gathering group details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/groups?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            # Export response to file for debugging only
            if DEBUG:
                with open(f"group_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            groups = data.get('groups', data.get('group', []))
            if not groups:
                break

            results.extend(groups)

            if len(groups) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching groups at offset {offset}: {e}")
            print(f"Error fetching groups at offset {offset}: {e}")
            break

    return results

def gather_network_details(session, base_url, verify=True):
    """
    Gather all networks from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of network data dictionaries limited to the requested fields
    """
    logger.info("Gathering network details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/networks?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"network_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            networks = data.get('networks', data.get('network', []))
            if not networks:
                break

            for network in networks:
                results.append({
                    'id': network.get('id'),
                    'name': network.get('name'),
                    'displayName': network.get('displayName'),
                    'category': network.get('category'),
                    'interfaceName': network.get('interfaceName'),
                    'bridgeName': network.get('bridgeName'),
                    'bridgeInterface': network.get('bridgeInterface'),
                    'externalId': network.get('externalId'),
                    'externalType': network.get('externalType'),
                    'vlanId': network.get('vlanId'),
                    'vSwitchName': network.get('vSwitchName')
                })

            if len(networks) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching networks at offset {offset}: {e}")
            print(f"Error fetching networks at offset {offset}: {e}")
            break

    return results

def gather_virtual_image_details(session, base_url, verify=True):
    """
    Gather all virtual images from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of virtual image data dictionaries
    """
    logger.info("Gathering virtual image details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/virtual-images?max={page_size}&offset={offset}&filterType=All&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"virtual_image_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            images = data.get('virtualImages', data.get('virtualImage', []))
            if not images:
                break

            results.extend(images)

            if len(images) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching virtual images at offset {offset}: {e}")
            print(f"Error fetching virtual images at offset {offset}: {e}")
            break

    return results

def gather_service_plan_details(session, base_url, verify=True):
    """
    Gather all service plans from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of service plan data dictionaries
    """
    logger.info("Gathering service plan details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/service-plans?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"service_plan_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            service_plans = data.get('servicePlans', data.get('servicePlan', []))
            if not service_plans:
                break

            results.extend(service_plans)

            if len(service_plans) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching service plans at offset {offset}: {e}")
            print(f"Error fetching service plans at offset {offset}: {e}")
            break

    return results

def gather_network_group_details(session, base_url, verify=True):
    """
    Gather all network groups from the Morpheus API

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of network group data dictionaries
    """
    logger.info("Gathering network group details")
    results = []
    page_size = 100
    offset = 0

    while True:
        try:
            url = f"{base_url}/api/networks/groups&max={page_size}&offset={offset}"
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open("network_groups_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            network_groups = data.get('networkGroups', data.get('networkGroup', data.get('networkgroups', [])))
            if not network_groups:
                break

            results.extend(network_groups)

            if len(network_groups) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching network groups: {e}")
            print(f"Error fetching network groups: {e}")
            break

    return results


def gather_network_domain_details(session, base_url, verify=True):
    """
    Gather all network domains from the Morpheus API

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of network domain data dictionaries
    """
    logger.info("Gathering network domain details")
    results = []
    page_size = 100
    offset = 0
    
    while True:
   
        url = f"{base_url}/api/networks/domains&max={page_size}&offset={offset}"
        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open("network_domains_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            network_domain = data.get('networkDomains', data.get('networkDomain', data.get('networkdomains', [])))
            if not network_domain:
                break

            results.extend(network_domain)

            if len(network_domain) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching network domains: {e}")
            print(f"Error fetching network domains: {e}")
            break    

    return results


def gather_instance_type_details(session, base_url, verify=True):
    """
    Gather all instance types from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of instance type data dictionaries
    """
    logger.info("Gathering instance type details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/library/instance-types?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"instance_type_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            instance_types = data.get('instanceTypes', data.get('instanceType', []))
            if not instance_types:
                break

            results.extend(instance_types)

            if len(instance_types) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching instance types at offset {offset}: {e}")
            print(f"Error fetching instance types at offset {offset}: {e}")
            break

    return results


def gather_cloud_type_details(session, base_url, verify=True):
    """
    Gather all cloud types from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of cloud type data dictionaries
    """
    logger.info("Gathering cloud type details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/zone-types?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"cloud_type_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            cloud_types = data.get('cloudTypes', data.get('cloudType', data.get('zoneTypes', data.get('zoneType', []))))
            if not cloud_types:
                break

            results.extend(cloud_types)

            if len(cloud_types) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching cloud types at offset {offset}: {e}")
            print(f"Error fetching cloud types at offset {offset}: {e}")
            break

    return results


def gather_layout_details(session, base_url, verify=True):
    """
    Gather all layouts from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of layout data dictionaries
    """
    logger.info("Gathering layout details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/library/layouts?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"layout_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            layouts = data.get('instanceTypeLayouts', data.get('layouts', data.get('layout', [])))
            if not layouts:
                break

            results.extend(layouts)

            if len(layouts) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching layouts at offset {offset}: {e}")
            print(f"Error fetching layouts at offset {offset}: {e}")
            break

    return results


def gather_cluster_details(session, base_url, verify=True):
    """
    Gather all clusters from the Morpheus API using pagination

    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        verify: Whether to verify SSL certificates (default: True)

    Returns:
        List of cluster data dictionaries
    """
    logger.info("Gathering cluster details")
    results = []
    page_size = 100
    offset = 0

    while True:
        url = f"{base_url}/api/clusters?max={page_size}&offset={offset}&sort=name&direction=asc"

        try:
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            if DEBUG:
                with open(f"cluster_offset_{offset}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)

            clusters = data.get('clusters', data.get('cluster', []))
            if not clusters:
                break

            results.extend(clusters)

            if len(clusters) < page_size:
                break

            offset += page_size
        except Exception as e:
            logger.error(f"Error fetching clusters at offset {offset}: {e}")
            print(f"Error fetching clusters at offset {offset}: {e}")
            break

    return results

def gather_datastore_details(session, base_url, datastores, verify=True):
    """
    Gather detailed information for each datastore by ID
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        datastores: List of datastore objects from API
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed datastore data dictionaries
    """
    results = []
    
    for datastore in datastores:
        if not datastore.get('id'):
            continue
        
        id = datastore['id']
        url = f"{base_url}/api/data-stores/{id}"
        
        try:
            # Make API call to get datastore details
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            # Export response to file for debugging only
            if DEBUG:
                with open(f"datastore_{id}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)
            
            if data and data.get('datastore'):
                datastore_data = data['datastore']
                
                # Remove containers and volumes from the result to reduce data size
                datastore_data.pop('tenants', None)
                datastore_data.pop('datastores', None)
                datastore_data.pop('resourcePermissions', None)
                
                results.append(datastore_data)
        except Exception as e:
            print(f"Error fetching details for datastore {id}: {e}")
            # Add basic datastore info if detailed fetch fails
            results.append(datastore)
    
    return results

def gather_storage_details(session, base_url, storages, verify=True):
    """
    Gather detailed information for each storage volume by ID
    
    Args:
        session: requests.Session object with authentication
        base_url: Base URL of the Morpheus appliance
        storages: List of storage objects from API
        verify: Whether to verify SSL certificates (default: True)
    
    Returns:
        List of detailed storage data dictionaries
    """
    results = []
    
    for storage in storages:
        if not storage.get('id'):
            continue
        
        id = storage['id']
        url = f"{base_url}/api/storage-volumes/{id}"
        
        try:
            # Make API call to get storage details
            response = session.get(url, timeout=30, verify=verify)
            response.raise_for_status()
            data = response.json()

            # Export response to file for debugging only
            if DEBUG:
                with open(f"storagevolume_{id}_response.json", 'w') as f:
                    json.dump(data, f, indent=2)
            
            if data and data.get('storageVolume'):
                storage_data = data['storageVolume']
                
                # Remove unnecessary data to reduce size
                storage_data.pop('tenants', None)
                storage_data.pop('datastores', None)
                storage_data.pop('resourcePermissions', None)
                
                results.append(storage_data)
        except Exception as e:
            print(f"Error fetching details for storage {id}: {e}")
            # Add basic storage info if detailed fetch fails
            results.append(storage)
    
    return results