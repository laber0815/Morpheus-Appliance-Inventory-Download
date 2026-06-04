# HPE Morpheus Appliance Inventory Download

A Python-based GUI application for connecting to HPE Morpheus Appliance via API and exporting comprehensive inventory data to multi-sheet Excel workbooks. This tool provides automated inventory gathering with detailed information extraction across clouds, cloud types, groups, networks, virtual images, service plans, network groups, network domains, layouts, instance types, clusters, hosts, instances, applications, datastores, and storage volumes.

<img width="795" height="776" alt="image" src="https://github.com/user-attachments/assets/2679aa49-b1cc-4201-bd62-490e34ed626b">

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Version History](#version-history)
- [Security Considerations](#security-considerations)
- [License](#license)

---

## Features

### Core Functionality
- **GUI-Based Operation**: Intuitive tkinter interface with no command-line knowledge required
- **Secure API Authentication**: Bearer token-based authentication with Morpheus API
- **Connection Testing**: Verify credentials and list available clouds before gathering inventory
- **Comprehensive Data Collection**: Gathers detailed information from 15 resource types
- **Multi-Sheet Excel Export**: Organizes data into separate sheets for easy analysis
- **Real-Time Progress Tracking**: Visual progress bar with status updates during operations
- **Integrated Logging**: Dual logging system (GUI display + detailed file logs)

### Data Gathering Capabilities
- **Cloud/Zone Details**: Zone types, status, location, server counts, statistics (paginated)
- **Cloud Types**: Available cloud types and their configurations
- **Groups**: Group inventory and metadata (paginated)
- **Networks**: Network inventory with interface, bridge, VLAN, and vSwitch fields (paginated)
- **Virtual Images**: Image catalog and metadata (paginated)
- **Service Plans**: Plan sizing and visibility data (paginated)
- **Network Groups**: Network grouping metadata (non-paginated)
- **Network Domains**: Domain-level networking metadata (non-paginated)
- **Layouts**: Layout catalog records from library endpoints (paginated)
- **Instance Types**: Instance type catalog records from library endpoints (paginated)
- **Clusters**: Kubernetes/container cluster data (paginated)
- **Host/Server Inventory**: Platform info, power state, CPU/memory stats, volumes (with detail fetching)
- **Instance Details**: Container-level data with IPs, server assignments, resource usage (with detail fetching)
- **Application Mapping**: Application configurations and associations
- **Datastore Details**: Storage repository information and capacity (with detail fetching)
- **Storage Volumes**: Volume-level storage details and allocations (with detail fetching)
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

## Installation

### Standard Installation

1. **Clone the repository:**
   ```powershell
   git clone https://github.hpe.com/lars-berger/Morpheus-Appliance-Inventory-Download.git
   cd Morpheus-Appliance-Inventory-Download
   ```

2. **Create virtual environment (recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # OR
   source venv/bin/activate     # Linux/macOS
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```powershell
   python hpe_morpheus_appliance_inventory.py
   ```

### Alternative: Standalone Executable

Pre-built Windows executables are available in the [Releases](releases/) section. No Python installation required.

---

## Usage

### Quick Start

1. **Launch the application:**
   ```powershell
   python hpe_morpheus_appliance_inventory.py
   ```

2. **Configure connection settings:**
   - **Morpheus URL**: Enter your appliance URL (e.g., `https://morpheus.company.com`)
   - **API Token**: Paste your API bearer token (obtain from Morpheus: Administration → User Settings → API Access)
   - **Debug Mode**: Optional checkbox to enable debug JSON export (useful for troubleshooting)
   - **Verify SSL Certificate**: Keep enabled for trusted certificates; disable only for lab/self-signed endpoints

<img width="772" height="125" alt="image" src="https://github.com/user-attachments/assets/35e50acb-f181-452f-ba04-e6a6377363d7" />

3. **Test connection:**
   - Click **Test Connection** button
   - Review cloud list in the log viewer
   - Verify accessibility before proceeding

4. **Configure export settings:**
   - **Output Directory**: Click **Browse** to select destination folder (default: Downloads)
   - **Excel Filename**: Specify output filename (default: `morpheus_inventory.xlsx`)

5. **Gather inventory:**
   - Click **Gather Inventory** button
   - Monitor progress bar and status messages
   - Wait for completion confirmation

<img width="777" height="107" alt="image" src="https://github.com/user-attachments/assets/ccdd420f-04a4-468a-b8c6-e91165be5a43" />

### Detailed Workflow

#### Step 1: Connection Configuration
Enter your Morpheus appliance details in the **Connection Settings** section:

| Field | Description | Example |
|-------|-------------|---------|
| **Morpheus URL** | Full URL of your Morpheus appliance | `https://morpheus.example.com` |
| **API Token** | Bearer token from Morpheus API Access | `eyJhbGciOiJIUzI1NiIs...` |
| **Debug Mode** | Enables detailed debug output and JSON snapshots in local `test/` files for troubleshooting API payloads | `Enabled` |
| **Verify SSL Certificate** | Enables TLS certificate verification for API requests; disable only when connecting to self-signed/test appliances | `Enabled` |

> **Note**: The URL should not include `/api` - this is added automatically by the application.

#### Debug and SSL Flags

Use these connection flags in the **Connection Settings** section:

- **Debug Mode**
   - When enabled, the application writes additional JSON response snapshots to the local `test/` folder.
   - Recommended for troubleshooting parsing/mapping issues or validating API payload content.
   - Keep disabled during normal operations to reduce extra debug output files.

- **Verify SSL Certificate**
   - When enabled (default), HTTPS requests validate the Morpheus appliance certificate chain.
   - Disable only for non-production environments using self-signed or otherwise untrusted certificates.
   - If disabled, TLS verification warnings may appear and your connection is less secure.

#### Step 2: Connection Testing
Click **Test Connection** to:
- Validate API credentials
- Verify network connectivity
- List available clouds/zones
- Display cloud details in log viewer

**Expected Output:**
```
[2025-12-16 14:30:15] ✓ Connection test successful - Found 3 cloud(s)
[2025-12-16 14:30:15] Cloud ID: 1 Name: Production AWS Type: Amazon Status: ok Location: us-east-1 Servers: 42
[2025-12-16 14:30:15] Cloud ID: 2 Name: Dev Azure Type: Microsoft Azure Status: ok Location: eastus Servers: 18
[2025-12-16 14:30:15] Cloud ID: 3 Name: VMware Cluster Type: VMware vCenter Status: ok Location: DC1 Servers: 156
```
<img width="790" height="778" alt="image" src="https://github.com/user-attachments/assets/d661ccbb-611c-44c9-99de-69659ccc9009" />



#### Step 3: Export Configuration
Configure where the inventory will be saved:

- **Output Directory**: Browse to select destination folder
  - Default: User's Downloads folder
  - Must have write permissions
  - Sufficient disk space required
  
- **Excel Filename**: Specify output file
  - Default: `morpheus_inventory.xlsx`
  - `.xlsx` extension added automatically if omitted
  - Existing files will be overwritten

#### Step 4: Inventory Gathering
Click **Gather Inventory** to begin data collection:

**Process Flow:**
1. Fetches base resource lists from 16 API endpoints
2. Gathers detailed information for each resource
3. Extracts and flattens nested data structures
4. Sanitizes data for Excel compatibility
5. Creates multi-sheet workbook
6. Saves to specified location

**Status Messages:**
```
Fetching clouds...
Gathering detailed cloud info (3 clouds)...
Fetching hosts...
Gathering detailed host info (216 hosts)...
Fetching instances...
Gathering detailed instance info (489 instances)...
...
Exporting to Excel...
Export complete: C:\Users\username\Downloads\morpheus_inventory.xlsx
```
<img width="788" height="793" alt="image" src="https://github.com/user-attachments/assets/011cf122-1cea-47f2-82b1-bbf6878c3236" />

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
- `id`, `name`, `code`, `instanceVersion`
- `description`, `creatable`, `sortOrder`

#### 9. **InstanceTypes Sheet**
Instance type inventory retrieved from paginated `/api/library/instance-types` endpoint.

**Sample Columns:**
- `id`, `name`, `code`, `description`
- `enabled`, `provisionType.code`, `featured`

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

#### 13. **CloudTypes Sheet**
Available cloud types and their configurations.

**Sample Columns:**
- `id`, `name`, `code`, `enabled`
- `category`, `active`, `visibility`
- `description`, `hasConfig`

#### 14. **Clusters Sheet**
Kubernetes and container orchestration clusters.

**Sample Columns:**
- `id`, `name`, `type`, `zone.name`
- `status`, `enabled`, `managed`
- `workerCount`, `masters`, `workers`

#### 15. **Datastores Sheet**
Storage datastores and repositories.

**Sample Columns:**
- `datastoreId`, `datastoreName`, `type`
- `zone.name`, `online`, `allowWrite`
- `freeSpace`, `capacity`, `permissions`

#### 16. **StorageVolumes Sheet**
Individual storage volumes and disks.

**Sample Columns:**
- `volumeId`, `volumeName`, `type`
- `zone.name`, `storageServer.name`
- `deviceName`, `maxStorage`, `active`

#### Debug Data (Optional)
When debug mode is enabled via the **Debug Mode** checkbox in Connection Settings, additional JSON files are exported:
- `cloud_list_offset_{offset}_response.json` - Raw cloud list page responses
- `cloud_type_offset_{offset}_response.json` - Raw cloud type page responses
- `cluster_offset_{offset}_response.json` - Raw cluster page responses
- `group_offset_{offset}_response.json` - Raw group page responses
- `network_offset_{offset}_response.json` - Raw network page responses
- `virtual_image_offset_{offset}_response.json` - Raw virtual image page responses
- `service_plan_offset_{offset}_response.json` - Raw service plan page responses
- `network_groups_response.json` - Raw network groups response
- `network_domains_response.json` - Raw network domains response
- `layout_offset_{offset}_response.json` - Raw layouts page responses
- `instance_type_offset_{offset}_response.json` - Raw instance type page responses
- `cloud_{id}_response.json` - Raw cloud detail API responses
- `host_{id}_response.json` - Raw host API responses
- `instance_{id}_response.json` - Raw instance API responses
- `datastore_{id}_response.json` - Raw datastore detail responses
- `storagevolume_{id}_response.json` - Raw storage volume detail responses

**Sample Excel Output:** [View example workbook](output/sample%20output.xlsx)

---

## Logging

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

---

## Troubleshooting

### Common Issues

**Problem: No data in Excel sheets**
```
Check:
    1. API token has sufficient permissions
    2. Resources exist in Morpheus (run Test Connection)
    3. Review log file for API errors
    4. Verify network connectivity to Morpheus appliance
```

### Log Analysis

Check detailed logs in `logs/` directory for:
- Full exception tracebacks
- API request/response details
- Data extraction issues
- File I/O errors

---

## Version History

### v0.2.14 (Current - 05/13/2026)
- Added Cloud Types gathering (`/api/cloud-types`) with pagination
- Modernized Clusters gathering with pagination and gather_steps integration
- Modernized Clouds gathering with dedicated `gather_cloud_list_details()` function
- Added Debug Mode checkbox to GUI for easy debug file export toggle
- Centralized debug control with single module-level `DEBUG` variable
- Expanded workbook export to include 16 sheets (added CloudTypes)
- All resource gathering now uses uniform paginated approach

### v0.2.13 (05/12/2026)
- Added groups, networks, virtual images, service plans, network groups, network domains, layouts, and instance type inventory gathering
- Expanded workbook export to include 15 sheets
- Updated gather workflow with paginated and non-paginated pre-fetch steps

### v0.2.4
- Integrated centralized logging system
- Enhanced error handling with full tracebacks
- Improved log message auto-leveling (error vs info)
- Updated version display in GUI footer

### v0.2.3
- Added horizontal scrollbar to log viewer
- Enhanced null-safe data extraction
- Improved ANSI code sanitization

### v0.2.1
- Unified resource gathering with generic function
- Removed duplicate gather_instance_details
- Implemented RESOURCE_CONFIG pattern

### v0.1.x
- Initial release with basic functionality
- Cloud, server, instance gathering
- Multi-sheet Excel export

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
Organization: Hewlett Packard Enterprise

---

## License

MIT License

Copyright (c) 2025 Hewlett Packard Enterprise

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [Report a bug or request a feature](https://github.com/laber0815/Morpheus-Appliance-Inventory-Download/issues)
- **Documentation**: [Morpheus API Reference](https://apidocs.morpheusdata.com/reference)
