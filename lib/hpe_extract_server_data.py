"""
Script to extract specific server data from Morpheus API JSON response
"""
# Application version information
__version__ = "0.1.23"
__build_date__ = "06/03/2026 09:55:47"
__author__ = "Lars Berger (lars.berger@hpe.com)"

import json
from pathlib import Path


def extract_server_data(data):
    """
    Extract specific fields from server JSON data - returns one object per server
    
    Args:
        data: Dictionary containing server data (either the full API response or just the server object)
        
    Returns:
        List containing a single dictionary with extracted server information
    """
    # Check if data has 'server' key or is already the server object
    if isinstance(data, dict) and 'server' in data:
        server = data.get('server', {})
    else:
        server = data
    
    # Create single server object
    server_obj = {
        'serverId': server.get('id'),
        'serverUuid': server.get('uuid'),
        'serverExternalId': server.get('externalId'),
        'serverName': server.get('name'),
        'hostname': server.get('hostname'),
        'accountId': server.get('accountId'),
        'account': {
            'id': (server.get('account') or {}).get('id'),
            'name': (server.get('account') or {}).get('name')
        },
        'zone': {
            'id': (server.get('zone') or {}).get('id'),
            'name': (server.get('zone') or {}).get('name'),
            'type': (server.get('zone') or {}).get('type')
        },
        'computeServerType': {
            'id': (server.get('computeServerType') or {}).get('id'),
            'code': (server.get('computeServerType') or {}).get('code'),
            'name': (server.get('computeServerType') or {}).get('name'),
            'managed': (server.get('computeServerType') or {}).get('managed'),
            'externalDelete': (server.get('computeServerType') or {}).get('externalDelete')
        },
        'platform': server.get('platform'),
        'platformVersion': server.get('platformVersion'),
        'maxCores': server.get('maxCores'),
        'coresPerSocket': server.get('coresPerSocket'),
        'maxMemory': server.get('maxMemory'),
        'maxStorage': server.get('maxStorage'),
        'powerState': server.get('powerState'),
        'status': server.get('status'),
        'agentInstalled': server.get('agentInstalled'),
        'agentVersion': server.get('agentVersion'),
        'serverOs': {
            'id': (server.get('serverOs') or {}).get('id'),
            'code': (server.get('serverOs') or {}).get('code'),
            'name': (server.get('serverOs') or {}).get('name'),
            'vendor': (server.get('serverOs') or {}).get('vendor'),
            'category': (server.get('serverOs') or {}).get('category'),
            'osFamily': (server.get('serverOs') or {}).get('osFamily'),
            'osVersion': (server.get('serverOs') or {}).get('osVersion'),
            'platform': (server.get('serverOs') or {}).get('platform')
        },
        'stats': {
            'usedStorage': (server.get('stats') or {}).get('usedStorage'),
            'maxStorage': (server.get('stats') or {}).get('maxStorage'),
            'usedMemory': (server.get('stats') or {}).get('usedMemory'),
            'maxMemory': (server.get('stats') or {}).get('maxMemory'),
            'freeMemory': (server.get('stats') or {}).get('freeMemory'),
            'cpuUsage': (server.get('stats') or {}).get('cpuUsage')
        },
        'config': {
            'cpuModel': (server.get('config') or {}).get('cpuModel'),
            'cpuCount': (server.get('config') or {}).get('cpuCount'),
            'cpuMhz': (server.get('config') or {}).get('cpuMhz'),
            'threadCount': (server.get('config') or {}).get('threadCount'),
            'nicCount': (server.get('config') or {}).get('nicCount'),
            'hardwareVendor': (server.get('config') or {}).get('hardwareVendor')
        }
    }
    
    return [server_obj]

