"""
HPE Morpheus Appliance Inventory Download
A GUI application for connecting to Morpheus API and exporting inventory to Excel
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import threading
import re
import sys
import platform

# Add lib directory to path
lib_path = Path(__file__).parent / 'lib'
sys.path.insert(0, str(lib_path))

# Import custom modules
from lib.hpe_morpheus_gather_detail import gather_cloud_list_details, gather_cloud_type_details, gather_server_details, gather_datastore_details, gather_storage_details, gather_instance_details, gather_group_details, gather_network_details, gather_virtual_image_details, gather_service_plan_details, gather_network_group_details, gather_network_domain_details, gather_layout_details, gather_instance_type_details, gather_cluster_details, set_debug
from lib import logger

# Application version information
__version__ = "0.2.19"
__build_date__ = "05/22/2026 14:18:39"
__author__ = "Lars Berger (lars.berger@hpe.com)"

class MorpheusInventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Morpheus Appliance Inventory Download v{__version__}")
        self.root.geometry("800x750")
        
        # Variables
        self.url_var = tk.StringVar() 
        self.token_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.excel_file_var = tk.StringVar(value="morpheus_inventory.xlsx")
        self.debug_var = tk.BooleanVar(value=False)
        self.verify_ssl_var = tk.BooleanVar(value=True)
        
        # API session
        self.session = None
        self.base_url = ""
        self.url_var.set('https://demo.morpheusdata.local/')
        self.token_var.set('user API token here')
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connection Section
        connection_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        connection_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(connection_frame, text="Morpheus URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        url_entry = ttk.Entry(connection_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        ttk.Label(connection_frame, text="API Token:").grid(row=1, column=0, sticky=tk.W, pady=2)
        token_entry = ttk.Entry(connection_frame, textvariable=self.token_var, width=50, show="*")
        token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        test_button = ttk.Button(connection_frame, text="Test Connection", command=self.test_connection)
        test_button.grid(row=1, column=2, padx=5)
        
        debug_checkbox = ttk.Checkbutton(connection_frame, text="Debug Mode", variable=self.debug_var)
        debug_checkbox.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        verify_ssl_checkbox = ttk.Checkbutton(connection_frame, text="Verify SSL Certificate", variable=self.verify_ssl_var)
        verify_ssl_checkbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        connection_frame.columnconfigure(1, weight=1)
        
        # Cloud List Section
        cloud_frame = ttk.LabelFrame(main_frame, text="Available Clouds / Log", padding="10")
        cloud_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create text widget without wrap and add horizontal scrollbar
        self.cloud_text = scrolledtext.ScrolledText(cloud_frame, height=15, width=70, wrap=tk.NONE)
        self.cloud_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(cloud_frame, orient=tk.HORIZONTAL, command=self.cloud_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.cloud_text.configure(xscrollcommand=h_scrollbar.set)
        
        clear_log_button = ttk.Button(cloud_frame, text="Clear Log", command=self.clear_error_log)
        clear_log_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        cloud_frame.rowconfigure(0, weight=1)
        cloud_frame.columnconfigure(0, weight=1)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Export Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=40)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        browse_button = ttk.Button(output_frame, text="Browse...", command=self.browse_directory)
        browse_button.grid(row=0, column=2, padx=5)
        
        ttk.Label(output_frame, text="Excel Filename:").grid(row=1, column=0, sticky=tk.W, pady=2)
        file_entry = ttk.Entry(output_frame, textvariable=self.excel_file_var, width=40)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        output_frame.columnconfigure(1, weight=1)
        
        # Progress Section
        progress_frame = ttk.Frame(main_frame, padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        progress_frame.columnconfigure(0, weight=1)
        
        # Action Button
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.gather_button = ttk.Button(action_frame, text="Gather Inventory", 
                                        command=self.gather_inventory, 
                                        style="Accent.TButton")
        self.gather_button.grid(row=0, column=0, pady=10)
        action_frame.columnconfigure(0, weight=1)
        
        # Version Info
        version_frame = ttk.Frame(main_frame)
        version_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        version_info = f"Version {__version__} | Build: {__build_date__}"
        version_label = ttk.Label(version_frame, text=version_info, 
                                  font=('TkDefaultFont', 8), foreground='gray')
        version_label.grid(row=0, column=0)
        version_frame.columnconfigure(0, weight=1)
        
        # Configure grid weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
    
    def create_session(self):
        """Create HTTP session with authentication headers"""
        url = self.url_var.get().strip().rstrip('/')
        token = self.token_var.get().strip()
        
        if not url or not token:
            messagebox.showerror("Error", "Please provide both URL and API Token")
            return False
        
        self.base_url = url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        
        return True
    
    def log_message(self, error_message, log_to_console=True):
        """
        Log error messages to the cloud text output box
        
        Args:
            error_message: The error message to log
            log_to_console: If True, also print to console
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {error_message}\n"
        
        # Add to cloud text box
        self.cloud_text.insert(tk.END, formatted_message)
        # Auto-scroll to the latest entry
        self.cloud_text.see(tk.END)
        
        # Also log to central logger
        if "✗" in error_message or "error" in error_message.lower():
            logger.error(error_message)
        else:
            logger.info(error_message)
    
    def clear_error_log(self):
        """Clear all messages from the cloud text output box"""
        self.cloud_text.delete(1.0, tk.END)
        self.log_message("Cloud/Log cleared", log_to_console=False)
    
    def test_connection(self):
        """Test connection to Morpheus API and list available clouds"""
        if not self.create_session():
            self.log_message("Failed to create session: Invalid URL or Token")
            return
        
        self.cloud_text.delete(1.0, tk.END)
        self.status_label.config(text="Testing connection...")
        self.root.update()
        
        try:
            # Test connection by listing clouds
            verify = self.verify_ssl_var.get()
            response = self.session.get(f"{self.base_url}/api/zones", timeout=10, verify=verify)
            response.raise_for_status()
            
            data = response.json()
            clouds = data.get('zones', [])
            
            if clouds:
                self.log_message(f"✓ Connection test successful - Found {len(clouds)} cloud(s)")
                
                for cloud in clouds:
                    cloud_info = (
                        f"Cloud ID: {cloud.get('id')} "
                        f"Name: {cloud.get('name')} "
                        f"Type: {cloud.get('zoneType', {}).get('name', 'N/A')} "
                        f"Status: {cloud.get('status', 'N/A')} "
                        f"Location: {cloud.get('location', 'N/A')} "
                        f"Servers: {cloud.get('serverCount', 0)}"
                    )
                    self.log_message(f"{cloud_info}")
                
                self.status_label.config(text="Connection test successful")
                messagebox.showinfo("Success", f"Connected successfully! Found {len(clouds)} cloud(s).")
            else:
                info_msg = f"Connection Successful! No clouds found."
                self.log_message(f"✓ {info_msg}")
                messagebox.showinfo("Success", info_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection failed: {str(e)}"
            self.status_label.config(text="Connection failed")
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Connection Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_label.config(text="Error occurred")
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def gather_inventory(self):
        """Start inventory gathering in a separate thread"""
        if not self.create_session():
            return
        
        # Validate output settings
        output_dir = Path(self.output_dir_var.get())
        if not output_dir.exists():
            error_msg = f"Output directory does not exist: {output_dir}"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            return
        
        excel_file = self.excel_file_var.get().strip()
        if not excel_file:
            error_msg = "Please provide an Excel filename"
            self.log_message(f"✗ {error_msg}")
            messagebox.showerror("Error", error_msg)
            return
        
        if not excel_file.endswith('.xlsx'):
            excel_file += '.xlsx'
        
        # Disable button during gathering
        self.gather_button.config(state='disabled')
        
        # Start gathering in separate thread
        thread = threading.Thread(target=self._gather_inventory_thread, 
                                  args=(output_dir / excel_file,))
        thread.daemon = True
        thread.start()
    
    def _gather_inventory_thread(self, output_file):
        """Background thread for gathering inventory"""
        try:
            # Set debug mode based on checkbox
            set_debug(self.debug_var.get())
            verify = self.verify_ssl_var.get()
            
            self.status_label.config(text="Gathering inventory data...")
            self.progress_var.set(0)
            
            # Gather data from API
            all_data = {}

            gather_steps = [
                ('clouds', 'Gathering cloud data...', gather_cloud_list_details),
                ('groups', 'Gathering group data...', gather_group_details),
                ('networks', 'Gathering network data...', gather_network_details),
                ('virtualimages', 'Gathering virtual image data...', gather_virtual_image_details),
                ('serviceplans', 'Gathering service plan data...', gather_service_plan_details),
                ('networkgroups', 'Gathering network group data...', gather_network_group_details),
                ('networkdomains', 'Gathering network domain data...', gather_network_domain_details),
                ('layouts', 'Gathering layout data...', gather_layout_details),
                ('instancetypes', 'Gathering instance type data...', gather_instance_type_details),
                ('cloudtypes', 'Gathering cloud type data...', gather_cloud_type_details),
                ('clusters', 'Gathering cluster data...', gather_cluster_details)
            ]

            endpoints = [
                ('hosts', '/api/servers?powerState=on&vmHypervisor=true&bareMetalHost=true&max=200'),
                ('instances', '/api/instances'),
                ('apps', '/api/apps'),
                ('datastores', '/api/data-stores'),
                ('storagevolumes', '/api/storage-volumes')
            ]
            
            total_steps = len(endpoints) + len(gather_steps)

            for idx, (name, status_text, gather_func) in enumerate(gather_steps):
                self.status_label.config(text=status_text)
                self.log_message(f"Start fetching {name}")
                self.root.update()

                try:
                    all_data[name] = gather_func(self.session, self.base_url, verify=verify)
                except Exception as e:
                    error_msg = f"Error fetching {name}: {str(e)}"
                    self.log_message(f"✗ {error_msg}")
                    logger.error(f"Failed to fetch {name}", exc_info=True)
                    all_data[name] = []

                self.progress_var.set((idx + 1) / total_steps * 50)
                self.root.update()
            
            for idx, (name, endpoint) in enumerate(endpoints):
                self.status_label.config(text=f"Fetching {name}...")
                self.log_message(f"Start fetching {name}")
                self.root.update()
                
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=30, verify=verify)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract the main data array
                    if name == 'instances':
                        instances = data.get('instances', [])                        # Gather detailed datastore information
                        if instances:
                            self.status_label.config(text=f"Gathering detailed instance info ({len(instances)} instances)...")
                            self.root.update()
                            all_data[name] = gather_instance_details(self.session, self.base_url, instances, verify=verify)
                        else:
                            all_data[name] = []
                    elif name == 'apps':
                        all_data[name] = data.get('apps', [])
                    elif name == 'hosts':
                        hosts = data.get('servers', [])
                        # Gather detailed host information
                        if hosts:
                            self.status_label.config(text=f"Gathering detailed host info ({len(hosts)} hosts)...")
                            self.root.update()
                            all_data[name] = gather_server_details(self.session, self.base_url, hosts, verify=verify)
                        else:
                            all_data[name] = []
                    elif name == 'datastores':
                        datastores = data.get('datastores', [])
                        # Gather detailed datastore information
                        if datastores:
                            self.status_label.config(text=f"Gathering detailed datastore info ({len(datastores)} datastores)...")
                            self.root.update()
                            all_data[name] = gather_datastore_details(self.session, self.base_url, datastores, verify=verify)
                        else:
                            all_data[name] = []
                    elif name == 'storagevolumes':
                        storages = data.get('storageVolumes', [])
                        # Gather detailed storage information
                        if storages:
                            self.status_label.config(text=f"Gathering detailed storage volumes ({len(storages)} storages)...")
                            self.root.update()
                            all_data[name] = gather_storage_details(self.session, self.base_url, storages, verify=verify)
                        else:
                            all_data[name] = []
                except Exception as e:
                    error_msg = f"Error fetching {name}: {str(e)}"
                    self.log_message(f"✗ {error_msg}")
                    logger.error(f"Failed to fetch {name}", exc_info=True)
                    all_data[name] = []
                
                self.progress_var.set((idx + len(gather_steps) + 1) / total_steps * 50)
                self.root.update()
            
            # Export to Excel
            self.status_label.config(text="Exporting to Excel...")
            self.root.update()
            
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Clouds sheet
                if all_data.get('clouds'):
                    clouds_df = self._flatten_data(all_data['clouds'])
                    clouds_df.to_excel(writer, sheet_name='Clouds', index=False)

                # Groups sheet
                if all_data.get('groups'):
                    groups_df = self._flatten_data(all_data['groups'])
                    groups_df.to_excel(writer, sheet_name='Groups', index=False)

                # Networks sheet
                if all_data.get('networks'):
                    networks_df = self._flatten_data(all_data['networks'])
                    networks_df.to_excel(writer, sheet_name='Networks', index=False)

                # Virtual images sheet
                if all_data.get('virtualimages'):
                    virtual_images_df = self._flatten_data(all_data['virtualimages'])
                    virtual_images_df.to_excel(writer, sheet_name='VirtualImages', index=False)

                # Service plans sheet
                if all_data.get('serviceplans'):
                    service_plans_df = self._flatten_data(all_data['serviceplans'])
                    service_plans_df.to_excel(writer, sheet_name='ServicePlans', index=False)

                # Network groups sheet
                if all_data.get('networkgroups'):
                    network_groups_df = self._flatten_data(all_data['networkgroups'])
                    network_groups_df.to_excel(writer, sheet_name='NetworkGroups', index=False)

                # Network domains sheet
                if all_data.get('networkdomains'):
                    network_domains_df = self._flatten_data(all_data['networkdomains'])
                    network_domains_df.to_excel(writer, sheet_name='NetworkDomains', index=False)

                # Layouts sheet
                if all_data.get('layouts'):
                    layouts_df = self._flatten_data(all_data['layouts'])
                    layouts_df.to_excel(writer, sheet_name='Layouts', index=False)

                # Instance types sheet
                if all_data.get('instancetypes'):
                    instance_types_df = self._flatten_data(all_data['instancetypes'])
                    instance_types_df.to_excel(writer, sheet_name='InstanceTypes', index=False)

                # Cloud types sheet
                if all_data.get('cloudtypes'):
                    cloud_types_df = self._flatten_data(all_data['cloudtypes'])
                    cloud_types_df.to_excel(writer, sheet_name='CloudTypes', index=False)
                
                self.progress_var.set(60)
                self.root.update()
                
                # Hosts/Server sheet
                if all_data.get('hosts'):
                    hosts_df = self._flatten_data(all_data['hosts'])
                    hosts_df.to_excel(writer, sheet_name='Hosts', index=False)
                
                self.progress_var.set(75)
                self.root.update()
                
                # Instances sheet
                if all_data.get('instances'):
                    instances_df = self._flatten_data(all_data['instances'])
                    instances_df.to_excel(writer, sheet_name='Instances', index=False)
                
                self.progress_var.set(90)
                self.root.update()

                # starting exporting other sheets into Excel
                
                # Apps sheet
                if all_data.get('apps'):
                    apps_df = self._flatten_data(all_data['apps'])
                    apps_df.to_excel(writer, sheet_name='Apps', index=False)
                
                # Cluster sheet
                if all_data.get('clusters'):
                    clusters_df = self._flatten_data(all_data['clusters'])
                    clusters_df.to_excel(writer, sheet_name='Clusters', index=False)

                # Cluster sheet
                if all_data.get('hosts'):
                    hosts_df = self._flatten_data(all_data['hosts'])
                    hosts_df.to_excel(writer, sheet_name='Hosts', index=False)

                # Cluster sheet
                if all_data.get('datastores'):
                    datastores_df = self._flatten_data(all_data['datastores'])
                    datastores_df.to_excel(writer, sheet_name='Datastores', index=False)
                self.progress_var.set(90)
                self.root.update()    
                # Storage Volumes sheet
                if all_data.get('storagevolumes'):
                    storagevolumes_df = self._flatten_data(all_data['storagevolumes'])
                    storagevolumes_df.to_excel(writer, sheet_name='StorageVolumes', index=False)

                self.progress_var.set(100)
                self.root.update()
            
            self.status_label.config(text=f"Export complete: {output_file}")
            self.log_message(f"✓ Inventory exported successfully to: {output_file}")
            logger.info(f"Inventory export completed: {output_file}")
            messagebox.showinfo("Success", f"Inventory exported successfully to:\n{output_file}")
            
        except Exception as e:
            error_msg = f"Failed to gather inventory: {str(e)}"
            self.status_label.config(text="Export failed")
            self.log_message(f"✗ {error_msg}")
            logger.exception("Inventory gathering failed")
            messagebox.showerror("Error", error_msg)
        
        finally:
            self.gather_button.config(state='normal')
            self.root.update()
    
    def _flatten_data(self, data_list):
        """Flatten nested JSON data for DataFrame"""
        flattened = []
        
        for item in data_list:
            flat_item = {}
            self._flatten_dict(item, flat_item, '')
            flattened.append(flat_item)
        
        return pd.DataFrame(flattened)
    
    def _sanitize_value(self, value):
        """Clean ANSI escape codes and Excel-incompatible characters from values"""
        if value is None:
            return ''
        
        # Convert to string
        str_value = str(value)
        
        # Remove ANSI escape codes (e.g., \x1b[0;35m or D[0;35m)
        # Pattern matches ESC codes like \x1b[...m or D[...m
        ansi_pattern = r'\x1b\[[0-9;]*m|D\[[0-9;]*m'
        str_value = re.sub(ansi_pattern, '', str_value)
        
        # Remove other control characters except newlines and tabs
        str_value = ''.join(char for char in str_value if ord(char) >= 32 or char in '\n\r\t')
        
        # Remove any remaining escape sequences
        str_value = re.sub(r'\x1b', '', str_value)
        
        return str_value.strip()
    
    def _flatten_dict(self, d, parent, prefix=''):
        """Recursively flatten nested dictionaries"""
        # Handle case where d is a list instead of dict
        if isinstance(d, list):
            if d and isinstance(d[0], dict):
                # If it's a list of dicts, convert to JSON string
                json_str = json.dumps(d)
                if prefix:
                    parent[prefix] = self._sanitize_value(json_str)
                return
            else:
                # If it's a simple list, convert to comma-separated string
                cleaned_list = [self._sanitize_value(v) for v in d]
                if prefix:
                    parent[prefix] = ', '.join(cleaned_list)
                return
        
        # Handle case where d is not a dict
        if not isinstance(d, dict):
            if prefix:
                parent[prefix] = self._sanitize_value(d)
            return
            
        for key, value in d.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._flatten_dict(value, parent, new_key)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Sanitize JSON string
                    json_str = json.dumps(value)
                    parent[new_key] = self._sanitize_value(json_str)
                else:
                    # Sanitize each list item
                    cleaned_list = [self._sanitize_value(v) for v in value]
                    parent[new_key] = ', '.join(cleaned_list)
            else:
                parent[new_key] = self._sanitize_value(value)


def main():
    logger.info(f"Application Version: {__version__}")
    logger.info(f"Build Date: {__build_date__}")
    logger.info(f"Client OS: {platform.platform()}")
    logger.info(f"Python Version: {sys.version.split()[0]}")
    logger.info(f"Tkinter Version: {tk.TkVersion}")

    root = tk.Tk()
    app = MorpheusInventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
