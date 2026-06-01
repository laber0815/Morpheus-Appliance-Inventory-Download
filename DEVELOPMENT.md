# Development - HPE Morpheus Appliance Inventory Download

A Python-based GUI application for connecting to HPE Morpheus Appliance via API and exporting comprehensive inventory data to multi-sheet Excel workbooks. This tool provides automated inventory gathering with detailed information extraction across clouds, hosts, instances, applications, clusters, networks, network groups, network domains, virtual images, layouts, service plans, datastores, and storage volumes.

<img width="793" height="778" alt="image" src="https://github.com/user-attachments/assets/e1619ed0-fd90-49b0-8b0c-76ef600d4681" />
---

## Table of Contents

- [Requirements](#requirements)
- [Functionality Overview](#functionality-overview)
- [Building Executable](#building-executable)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [License](#license)

---

## Requirements

### System Requirements
- **Operating System**: Windows, Linux, or macOS
- **Python Version**: Python 3.11 or higher (tested with 3.11+)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large inventories)
- **Disk Space**: 100MB minimum for application + logs + exports

### Python Dependencies

**Core Libraries:**
```
requests>=2.31.0       # HTTP API communication
pandas>=2.0.0          # Data manipulation and Excel export
openpyxl>=3.1.0        # Excel file format support
```

**Standard Library Modules:**
- `tkinter` - GUI framework (included with Python)
- `threading` - Background task processing
- `json` - JSON data handling
- `pathlib` - File path operations
- `logging` - Centralized logging
- `re` - Regular expressions for sanitization
- `datetime` - Timestamp generation

### Network Requirements
- HTTPS access to Morpheus Appliance API endpoint
- Valid SSL certificate (or ability to handle self-signed certificates)
- API timeout tolerance: 30 seconds per request

---

## Functionality Overview

### Data Collection Architecture

The application uses a modular architecture with specialized extraction functions:

```
hpe_morpheus_appliance_inventory.py (Main GUI)
    ├── lib/hpe_morpheus_gather_detail.py (Generic gathering logic)
    │   ├── gather_cloud_list_details()
    │   ├── gather_cloud_type_details()
    │   ├── gather_cluster_details()
    │   ├── gather_group_details()
    │   ├── gather_network_details()
    │   ├── gather_network_group_details()
    │   ├── gather_network_domain_details()
    │   ├── gather_virtual_image_details()
    │   ├── gather_layout_details()
    │   ├── gather_instance_type_details()
    │   ├── gather_service_plan_details()
    │   ├── gather_server_details()
    │   ├── gather_instance_details()
    │   ├── gather_datastore_details()
    │   ├── gather_storage_details()
    │   ├── set_debug()
    ├── lib/hpe_extract_cloud_data.py (Cloud data extraction)
    ├── lib/hpe_extract_server_data.py (Server data extraction)
    ├── lib/hpe_extract_instance_data.py (Instance data extraction)
    └── lib/logger.py (Centralized logging)
```

### API Endpoints

The application queries the following Morpheus API endpoints:

| Resource | Endpoint | Response Key | Details Endpoint |
|----------|----------|--------------|------------------|
| **Clouds** | `/api/zones` | `zones` | N/A (paginated list) |
| **Cloud Types** | `/api/zone-types` | `cloudTypes` | N/A (paginated list) |
| **Groups** | `/api/groups` | `groups` | N/A |
| **Networks** | `/api/networks` | `networks` | N/A |
| **Network Groups** | `/api/networks/groups` | `networkGroups` | N/A |
| **Network Domains** | `/api/networks/domains` | `networkDomains` | N/A |
| **Virtual Images** | `/api/virtual-images` | `virtualImages` | N/A |
| **Layouts** | `/api/library/layouts` | `layouts` | N/A |
| **Instance Types** | `/api/library/instance-types` | `instanceTypes` | N/A |
| **Service Plans** | `/api/service-plans` | `servicePlans` | N/A |
| **Clusters** | `/api/clusters` | `clusters` | N/A (paginated list) |
| **Hosts** | `/api/servers?powerState=on&vmHypervisor=true&bareMetalHost=true&max=200` | `servers` | `/api/servers/{id}` |
| **Instances** | `/api/instances` | `instances` | `/api/instances/{id}` |
| **Apps** | `/api/apps` | `apps` | N/A |
| **Datastores** | `/api/data-stores` | `datastores` | `/api/data-stores/{id}` |
| **Storage Volumes** | `/api/storage-volumes` | `storageVolumes` | `/api/storage-volumes/{id}` |

### Data Extraction Logic

**Cloud/Zone Extraction:**
- Zone ID, name, code, description
- Zone type details (code, name, enabled status)
- Cloud status, location, visibility
- Server count and capacity statistics
- Agent installation status

**Server/Host Extraction:**
- Server ID, name, external ID, platform
- Account/tenant information
- Zone association and compute type
- Power state, OS details, date created
- CPU/memory statistics
- Associated volumes (flattened)

**Instance Extraction (Container-Based):**
- Creates one object per container (not per instance)
- Instance ID, name, type, environment
- Tenant and cloud assignments
- Container-specific details:
  - Container ID, name, IP address
  - Server assignment and OS
  - Resource statistics (storage, memory, CPU)
  - Status and availability

**Datastore Extraction:**
- Datastore ID, name, type
- Zone assignment and configuration
- Capacity and usage statistics
- Online status and permissions

**Network Extraction:**
- Network ID, name, display name, category
- Interface and bridge metadata
- External identity and type fields
- VLAN and vSwitch information

**Network Group Extraction:**
- Group identifiers and naming metadata
- Association fields and visibility data where available

**Network Domain Extraction:**
- Domain identifiers and naming metadata
- Domain/network linkage and account-scoped metadata where available

**Virtual Image Extraction:**
- Image ID, name, code, category, and status metadata
- Image type and source-related identifiers

**Layout Extraction:**
- Layout identifiers, names, and codes
- Provisioning and version metadata where available

**Instance Type Extraction:**
- Instance type ID, name, code, and category
- Technology and provider identifiers
- Visibility and active/featured flags

**Service Plan Extraction:**
- Plan ID, name, code, active/visibility flags
- Resource sizing metadata such as memory/storage/cores where available

**Storage Volume Extraction:**
- Volume ID, name, type
- Zone and storage server details
- Device name and configuration
- Capacity and active status

### Data Processing Features

**Null-Safe Nested Access:**
```python
# Handles null values in nested objects
(server.get('account') or {}).get('name', '')
```

**ANSI Code Sanitization:**
```python
# Removes terminal escape codes like \x1b[0;35m
ansi_pattern = r'\x1b\[[0-9;]*m|D\[[0-9;]*m'
clean_value = re.sub(ansi_pattern, '', raw_value)
```

**Dictionary Flattening:**
```python
# Converts nested JSON to flat structure
{"stats": {"memory": {"used": 4096}}} 
→ {"stats.memory.used": 4096}
```

---

## Output Structure

### Excel Workbook Sheets

The exported Excel file contains up to 16 sheets:

#### 1. **Clouds Sheet**
Cloud/zone inventory with zone types and statistics.

**Sample Columns:**
- `cloudId`, `cloudName`, `cloudCode`, `description`
- `zoneType.id`, `zoneType.name`, `zoneType.code`
- `status`, `location`, `visibility`, `serverCount`
- `stats.serverCounts.all`, `stats.serverCounts.host`

#### 2. **Groups Sheet**
Group inventory retrieved from the paginated `/api/groups` endpoint.

**Sample Columns:**
- `id`, `name`, `description`, `uuid`
- `location`, `visibility`, `enabled`
- `owner.name`, `account.name`

#### 3. **Networks Sheet**
Network inventory retrieved from the paginated `/api/networks` endpoint.

**Sample Columns:**
- `id`, `name`, `displayName`, `category`
- `interfaceName`, `bridgeName`, `bridgeInterface`
- `externalId`, `externalType`, `vlanId`, `vSwitchName`

#### 4. **VirtualImages Sheet**
Virtual image inventory retrieved from the paginated `/api/virtual-images` endpoint.

**Sample Columns:**
- `id`, `name`, `code`, `category`, `status`
- `imageType`, `externalId`, `owner`, `visibility`

#### 5. **ServicePlans Sheet**
Service plan inventory retrieved from the paginated `/api/service-plans` endpoint.

**Sample Columns:**
- `id`, `name`, `code`, `active`, `visibility`
- `maxMemory`, `maxStorage`, `maxCores`, `customMaxStorage`

#### 6. **NetworkGroups Sheet**
Network group inventory retrieved from `/api/networks/groups`.

**Sample Columns:**
- `id`, `name`, `description`, `code`
- `visibility`, `account.id`, `account.name`

#### 7. **NetworkDomains Sheet**
Network domain inventory retrieved from `/api/networks/domains`.

**Sample Columns:**
- `id`, `name`, `description`, `fqdn`
- `visibility`, `account.id`, `account.name`

#### 8. **Layouts Sheet**
Layout inventory retrieved from paginated `/api/library/layouts` endpoint.

**Sample Columns:**
- `id`, `name`, `code`, `provisionType`
- `version`, `labels`, `visibility`

#### 9. **InstanceTypes Sheet**
Instance type inventory retrieved from paginated `/api/library/instance-types` endpoint.

**Sample Columns:**
- `id`, `name`, `code`, `category`, `technology`
- `featured`, `active`, `visibility`, `provisionType`

#### 10. **Hosts Sheet**
Physical and virtual host inventory.

**Sample Columns:**
- `serverId`, `serverName`, `externalId`, `platform`
- `account.id`, `account.name`, `zone.name`
- `computeServerType.name`, `serverOs.name`
- `powerState`, `maxCores`, `maxMemory`
- `stats.usedMemory`, `stats.usedStorage`

#### 11. **Instances Sheet**
Virtual machine and container instances (one row per container).

**Sample Columns:**
- `instanceId`, `instanceName`, `instanceType`
- `tenant.name`, `cloud.name`, `environment`
- `containerId`, `containerName`, `containerIp`
- `server.name`, `serverOs.name`
- `stats.usedStorage`, `stats.maxMemory`

#### 12. **Apps Sheet**
Application blueprints and app instances.

**Sample Columns:**
- `id`, `name`, `description`, `type`
- `status`, `environment`, `accountId`
- `instanceCount`, `containerCount`

#### 13. **Clusters Sheet**
Kubernetes and container orchestration clusters.

**Sample Columns:**
- `id`, `name`, `type`, `zone.name`
- `status`, `enabled`, `managed`
- `workerCount`, `masters`, `workers`

#### 14. **Datastores Sheet**
Storage datastores and repositories.

**Sample Columns:**
- `datastoreId`, `datastoreName`, `type`
- `zone.name`, `online`, `allowWrite`
- `freeSpace`, `capacity`, `permissions`

#### 15. **StorageVolumes Sheet**
Individual storage volumes and disks.

**Sample Columns:**
- `volumeId`, `volumeName`, `type`
- `zone.name`, `storageServer.name`
- `deviceName`, `maxStorage`, `active`

#### 9. **Debug Data (Optional)**
When debug mode is enabled, additional JSON files are exported:
- `cloud_list_offset_{offset}_response.json` - Raw cloud list page responses
- `cloud_type_offset_{offset}_response.json` - Raw cloud type page responses
- `cluster_offset_{offset}_response.json` - Raw cluster page responses
- `group_offset_{offset}_response.json` - Raw group page responses
- `network_offset_{offset}_response.json` - Raw network page responses
- `virtual_image_offset_{offset}_response.json` - Raw virtual image page responses
- `service_plan_offset_{offset}_response.json` - Raw service plan page responses
- `layout_offset_{offset}_response.json` - Raw layout page responses
- `instance_type_offset_{offset}_response.json` - Raw instance type page responses
- `network_groups_response.json` - Raw network groups response
- `network_domains_response.json` - Raw network domains response
- `cloud_{id}_response.json` - Raw cloud detail API responses
- `host_{id}_response.json` - Raw host API responses
- `instance_{id}_response.json` - Raw instance API responses
- `datastore_{id}_response.json` - Raw datastore detail responses
- `storagevolume_{id}_response.json` - Raw storage volume detail responses

![Excel Output](docs/screenshots/excel-output.png)
*Screenshot: Multi-sheet Excel workbook structure*

---

## Building Executable

### Using PyInstaller

**Directory Mode (Recommended):**
```powershell
pyinstaller --windowed --name "Morpheus Inventory" --icon=morpheus.ico .\hpe_morpheus_appliance_inventory.py
```

**Using Spec File:**
```powershell
pyinstaller morpheus_inventory.spec
```

The spec file includes:
- Hidden imports for pandas, numpy, openpyxl
- Library folder inclusion
- UPX compression
- No console window (GUI only)

**Output:**
- Directory mode: `dist/Morpheus Inventory/` folder with executable + dependencies
- Spec file: `dist/hpe_morpheus_appliance_inventory.exe`

### Distribution
Package the entire `dist/Morpheus Inventory/` folder for distribution. Users can run the .exe without Python installed.

---

## Troubleshooting

### Debugging

**Debug Mode:**
- Enable via the **Debug Mode** checkbox in the Connection Settings section of the GUI
- When enabled, JSON response files are exported for each API page/request
- Debug files are saved in the same directory as the application
- Useful for troubleshooting API response issues or analyzing raw data

**Programmatic Debug Control:**
```python
from lib.hpe_morpheus_gather_detail import set_debug
set_debug(True)   # Enable debug mode
set_debug(False)  # Disable debug mode
```
### Dual Logging System

The application maintains two logging outputs:

#### 1. GUI Log Viewer
- Displays in the "Available Clouds / Log" text area
- Shows timestamped messages with ✓ (success) or ✗ (error) indicators
- Scrollable with horizontal scrollbar for long messages
- Clearable via "Clear Log" button

#### 2. File Logging
- Location: `logs/morpheus_inventory_YYYYMMDD_HHMMSS.log`
- Level: DEBUG (captures all details)
- Format: `YYYY-MM-DD HH:MM:SS - module:line - LEVEL - message`
- Includes full exception tracebacks

**Sample Log File:**
```
2025-12-16 14:30:15 - hpe_morpheus_appliance_inventory:156 - INFO - Connection test successful - Found 3 cloud(s)
2025-12-16 14:35:42 - hpe_morpheus_gather_detail:78 - DEBUG - Fetching details for cloud ID: 1
2025-12-16 14:35:43 - hpe_morpheus_gather_detail:89 - DEBUG - Writing debug file: cloud_1_response.json
2025-12-16 14:42:18 - hpe_morpheus_appliance_inventory:412 - INFO - Inventory export completed: C:\Users\user\Downloads\morpheus_inventory.xlsx
```

### Log Management
- Logs are timestamped and never overwrite each other
- Old logs can be safely deleted manually
- No automatic log rotation (manage manually if disk space is limited)

### Common Issues

**Problem: "Connection failed: SSL Certificate verification failed"**
```
Solution: Add SSL verification bypass (for testing only):
    self.session.verify = False
    import urllib3
    urllib3.disable_warnings()
```

**Problem: "cannot be used in worksheets" Excel error**
```
Cause: ANSI escape codes in API response data
Solution: Already handled by _sanitize_value() function
```

**Problem: "'NoneType' object has no attribute 'get'"**
```
Cause: Null values in nested API objects
Solution: Use (obj.get('key') or {}).get() pattern (already implemented)
```

**Problem: PyInstaller "ordinal 380 not found in DLL"**
```
Solution: Use directory mode instead of --onefile:
    pyinstaller --windowed --name "Morpheus Inventory" .\hpe_morpheus_appliance_inventory.py
```

**Problem: No data in Excel sheets**
```
Check:
    1. API token has sufficient permissions
    2. Resources exist in Morpheus (run Test Connection)
    3. Review log file for API errors
    4. Verify network connectivity to Morpheus appliance
```

### Debug Mode

Enable detailed debugging:

1. **Set environment variable:**
   ```powershell
   $env:DEBUG = "1"
   ```

2. **Run application** - JSON response files will be written to working directory

3. **Review JSON files:**
   - `cloud_{id}_response.json`
   - `host_{id}_response.json`
   - `instance_{id}_response.json`

### Log Analysis

Check detailed logs in `logs/` directory for:
- Full exception tracebacks
- API request/response details
- Data extraction issues
- File I/O errors

---

## Security Considerations

### API Token Protection
- **Never commit tokens** to version control
- **Store securely** using environment variables or credential managers
- **Rotate regularly** per organizational security policies
- **Use read-only tokens** when possible (Morpheus supports scoped tokens)

### Network Security
- Application uses HTTPS for all API communications
- SSL certificate validation enabled by default
- Supports corporate proxy configurations (via environment variables)

### Data Handling
- Inventory data may contain sensitive information
- Excel files are not encrypted by default
- Store output files in secure locations
- Follow organizational data retention policies

### Logging
- Log files contain API endpoint URLs (not tokens)
- May include server names, IPs, and configuration details
- Secure log directory with appropriate file permissions

---

## Author

**Lars Berger**  
Email: lars.berger@hpe.com  
Organization: Hewlett Packard Enterprise

---

## License

MIT License

Copyright (c) 2025 Lars Berger / Hewlett Packard Enterprise

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [Report a bug or request a feature](https://github.com/laber0815/Morpheus-Appliance-Inventory-Download/issues)
- **Documentation**: [Morpheus API Reference](https://apidocs.morpheusdata.com/reference)
