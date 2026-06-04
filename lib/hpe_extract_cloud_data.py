"""
Script to extract specific cloud data from Morpheus API JSON response
"""
# Application version information
__version__ = "0.1.23"
__build_date__ = "06/04/2026 12:59:44"
__author__ = "Lars Berger (lars.berger@hpe.com)"

import json
from pathlib import Path


def extract_cloud_data(data):
    """
    Extract specific fields from cloud/zone JSON data
    
    Args:
        data: Dictionary containing cloud data (either the full API response or just the zone object)
        
    Returns:
        List containing a single dictionary with extracted cloud information
    """
    # Check if data has 'zone' key or is already the zone object
    if isinstance(data, dict) and 'zone' in data:
        cloud = data.get('zone', {})
    else:
        cloud = data
    
    # Extract cloud/zone data
    cloud_obj = {
        'cloudId': cloud.get('id'),
        'cloudName': cloud.get('name'),
        'cloudType': cloud.get('type'),
        'zoneType': {
            'id': cloud.get('zoneType', {}).get('id'),
            'name': cloud.get('zoneType', {}).get('name'),
            'code': cloud.get('zoneType', {}).get('code')
        },
        'status': cloud.get('status'),
        'enabled': cloud.get('enabled'),
        'location': cloud.get('location'),
        'regionCode': cloud.get('regionCode'),
        'visibility': cloud.get('visibility'),
        'stats': {
            'serverCounts': {
                'all': cloud.get('stats', {}).get('serverCounts', {}).get('all'),
                'host': cloud.get('stats', {}).get('serverCounts', {}).get('host'),
                'hypervisor': cloud.get('stats', {}).get('serverCounts', {}).get('hypervisor'),
                'containerHost': cloud.get('stats', {}).get('serverCounts', {}).get('containerHost'),
                'vm': cloud.get('stats', {}).get('serverCounts', {}).get('vm'),
                'baremetal': cloud.get('stats', {}).get('serverCounts', {}).get('baremetal'),
                'unmanaged': cloud.get('stats', {}).get('serverCounts', {}).get('unmanaged')
            }
        },
        'dateCreated': cloud.get('dateCreated'),
        'lastUpdated': cloud.get('lastUpdated')
    }
    
    return [cloud_obj]


