"""
Script to extract specific instance data from Morpheus API JSON response
"""
# Application version information
__version__ = "0.1.32"
__build_date__ = "06/04/2026 12:59:45"
__author__ = "Lars Berger (lars.berger@hpe.com)"

import json
from pathlib import Path


def extract_instance_data(data):
    """
    Extract specific fields from instance JSON data and create separate objects for each container
    
    Args:
        data: Dictionary containing instance data (either the full API response or just the instance object)
        
    Returns:
        List of dictionaries, one for each container with extracted instance and container information
    """
    # Check if data has 'instance' key or is already the instance object
    if isinstance(data, dict) and 'instance' in data:
        instance = data.get('instance', {})
    else:
        instance = data
    
    # Get container details
    container_details = instance.get('containerDetails', [])
    
    # If no containers, return single object with instance data
    if not container_details:
        return [{
            'instanceId': instance.get('id'),
            'instanceUuid': instance.get('uuid'),
            'instanceAccountId': instance.get('accountId'),
            'instanceName': instance.get('name'),
            'tenant': {
                'id': (instance.get('tenant') or {}).get('id'),
                'name': (instance.get('tenant') or {}).get('name')
            },
            'instanceType': {
                'id': (instance.get('instanceType') or {}).get('id'),
                'code': (instance.get('instanceType') or {}).get('code'),
                'category': (instance.get('instanceType') or {}).get('category'),
                'name': (instance.get('instanceType') or {}).get('name'),
                'image': (instance.get('instanceType') or {}).get('image')
            },
            'cloud': {
                'id': (instance.get('cloud') or {}).get('id'),
                'name': (instance.get('cloud') or {}).get('name'),
                'type': (instance.get('cloud') or {}).get('type')
            },
            'maxMemory': instance.get('maxMemory'),
            'maxStorage': instance.get('maxStorage'),
            'maxCores': instance.get('maxCores'),
            'coresPerSocket': instance.get('coresPerSocket'),
            'instanceStatus': instance.get('status'),
            'stats': {
                'usedStorage': (instance.get('stats') or {}).get('usedStorage'),
                'maxStorage': (instance.get('stats') or {}).get('maxStorage'),
                'usedMemory': (instance.get('stats') or {}).get('usedMemory'),
                'maxMemory': (instance.get('stats') or {}).get('maxMemory'),
                'usedCpu': (instance.get('stats') or {}).get('usedCpu'),
                'cpuUsage': (instance.get('stats') or {}).get('cpuUsage'),
                'cpuUsagePeak': (instance.get('stats') or {}).get('cpuUsagePeak'),
                'cpuUsageAvg': (instance.get('stats') or {}).get('cpuUsageAvg')
            }
        }]
    
    # Create one object per container
    result = []
    for container in container_details:
        server = container.get('server') or {}
        server_os = server.get('serverOs') or {}
        
        container_obj = {
            'instanceId': instance.get('id'),
            'instanceUuid': instance.get('uuid'),
            'instanceAccountId': instance.get('accountId'),
            'instanceName': instance.get('name'),
            'tenant': {
                'id': (instance.get('tenant') or {}).get('id'),
                'name': (instance.get('tenant') or {}).get('name')
            },
            'instanceType': {
                'id': (instance.get('instanceType') or {}).get('id'),
                'code': (instance.get('instanceType') or {}).get('code'),
                'category': (instance.get('instanceType') or {}).get('category'),
                'name': (instance.get('instanceType') or {}).get('name'),
                'image': (instance.get('instanceType') or {}).get('image')
            },
            'cloud': {
                'id': (instance.get('cloud') or {}).get('id'),
                'name': (instance.get('cloud') or {}).get('name'),
                'type': (instance.get('cloud') or {}).get('type')
            },
            'maxMemory': instance.get('maxMemory'),
            'maxStorage': instance.get('maxStorage'),
            'maxCores': instance.get('maxCores'),
            'coresPerSocket': instance.get('coresPerSocket'),
            'instanceStatus': instance.get('status'),
            'stats': {
                'usedStorage': (instance.get('stats') or {}).get('usedStorage'),
                'maxStorage': (instance.get('stats') or {}).get('maxStorage'),
                'usedMemory': (instance.get('stats') or {}).get('usedMemory'),
                'maxMemory': (instance.get('stats') or {}).get('maxMemory'),
                'usedCpu': (instance.get('stats') or {}).get('usedCpu'),
                'cpuUsage': (instance.get('stats') or {}).get('cpuUsage'),
                'cpuUsagePeak': (instance.get('stats') or {}).get('cpuUsagePeak'),
                'cpuUsageAvg': (instance.get('stats') or {}).get('cpuUsageAvg')
            },
            'containerId': container.get('id'),
            'containerName': container.get('name'),
            'containerIp': container.get('ip'),
            'server': {
                'platform': server.get('platform'),
                'platformVersion': server.get('platformVersion'),
                'externalId': server.get('externalId'),
                'powerState': server.get('powerState'),
                'serverOs': {
                    'name': server_os.get('name'),
                    'vendor': server_os.get('vendor'),
                    'osFamily': server_os.get('osFamily'),
                    'platform': server_os.get('platform')
                }
            }
        }
        result.append(container_obj)
    
    return result


