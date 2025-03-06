# This script connects to HPE-SAN-Storages, call the Host list and saves the output to a CSV file locally

# created:      Payam Avarwand - 24.01.2025
# last change:  Payam Avarwand - 07.02.2025

################# import_Libs #################
import subprocess
import sys
import importlib.util
REQUIRED = [
    "os",
    "sys",
    "subprocess",
    "paramiko",
    "base64",
    "re",
]
#------------------------------------------------------------#

def check_and_install_libraries():
    for lib in REQUIRED:
        if importlib.util.find_spec(lib) is None:
            print(f"Installing {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

        globals()[lib] = importlib.import_module(lib)
#------------------------------------------------------------#

check_and_install_libraries()
import os
import sys
import subprocess
import paramiko
import base64
import re

#####################################################################################################
# Decode
def decode_from_base64(encoded_string):
    return base64.b64decode(encoded_string.encode("utf-8")).decode("utf-8")

#####################################################################################################
# Ensure the directory exists
output_file_base_path = "D:\\HPE_Host\\"

if not os.path.exists(output_file_base_path):
    os.makedirs(output_file_base_path)
    print(f"Created: {output_file_base_path}")

#####################################################################################################
# List of device details (IP addresses)
enP = "UH90JbTE0gw"
enC = "c2hvd2hvc3Q="
enU = "MFfgjyhdbQ="
command = decode_from_base64(enC)
username = decode_from_base64(enU)
password = decode_from_base64(enP)

devices = [
    {"hostname": "10.10.10.11", "username": username, "password": password,},
    {"hostname": "10.10.10.10", "username": username, "password": password},
	{"hostname": "10.10.10.9", "username": username, "password": password,},
	{"hostname": "10.10.10.8", "username": username, "password": password,},
    {"hostname": "10.10.10.7", "username": username, "password": password,},
    {"hostname": "10.10.10.4", "username": username, "password": password,},
    {"hostname": "10.10.10.1", "username": username, "password": password,},
    {"hostname": "10.10.10.2", "username": username, "password": password,},
    {"hostname": "10.10.10.3", "username": username, "password": password,},
    {"hostname": "10.10.10.6", "username": username, "password": password,},
    {"hostname": "10.10.10.5", "username": username, "password": password,},
]

#####################################################################################################
# Iterate through devices
for device in devices:
    hostname = device["hostname"]
    username = device["username"]
    password = device["password"]
    output_file = f"{output_file_base_path}showhost_{hostname.replace('.', '_')}.csv"
    
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add the device's host key (not recommended for production)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the device
        ssh.connect(hostname=hostname, port=22, username=username, password=password)
        print(f"Connected to {hostname}")
        
        # Run the command
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        
        # Check for errors
        if error:
            print(f"Error running command on {hostname}: {error}")
        else:
            # Process the output to extract the second column, ignoring unwanted words and patterns
            filtered_lines = []
            for line in output.splitlines():
                # Ignore lines that contain 'Name' or 'total'
                if "Name" in line or "total" in line or "--" in line:
                    continue
                
                # Split the line into columns
                columns = line.split()
                
                # Check if the line has at least two columns
                if len(columns) >= 2:
                    second_column = columns[1].strip()
                    
                    # Remove any patterns like <number>:<number>:<number> in the second column
                    second_column = re.sub(r'\d+:\d+:\d+', '', second_column).strip()
                    
                    # Only add the line if the second column is not empty
                    if second_column:
                        filtered_lines.append(second_column)
            
            # Save the filtered result to a file for each device
            with open(output_file, "w") as file:
                file.write("\n".join(filtered_lines))
            print(f"Filtered and saved to {output_file}")
        
        # Close the SSH connection
        ssh.close()

    except Exception as e:
        print(f"An error occurred when processing {hostname}: {e}")