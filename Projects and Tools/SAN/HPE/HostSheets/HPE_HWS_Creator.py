''' This Script:
    queries the Host-Devices conntected to all desired Storages directly (3PAR or Primera?) --> extracts the Hostnames of them,
    asks for the report file from SANnav,
    merges the extracted Hostnames with corresponding imported data from the SANnav report,
    sorts the information according to required pattern for the HostWorkSheet Process.
    asks for the physical Server List from CMDB,
    adds the OS to the final sorted table.
'''

# created:      Avarwand - 07.02.2025
# last change:  Avarwand - 18.02.2025

################# Lib-Check and import #################
import sys
import subprocess
import importlib.util
REQUIRED = [
    "keyboard",
    "os",
    "sys",
    "importlib.util",
    "subprocess",
    "paramiko",
    "signal",
    "base64",
    "re",
    "csv",
    "tkinter",
    "datetime",
    "time"
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
import keyboard
import signal
import base64
import os
import paramiko
import re
import csv
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import time

#####################################################################################################
# V a r i a b l e s

today_date = datetime.now().strftime("%d-%m-%Y")
temp_dir = "C:\\temp" ; m_drve = "D:\\"
tilOS = os.path.join(temp_dir, f"a.csv")
output_raw = os.path.join(temp_dir, "vlbl.csv")
laniF = os.path.join(temp_dir, "fnl.csv")
merged = os.path.join(temp_dir, "mrgd.csv")

temp_files = [
    tilOS,
    output_raw,
    laniF,
    merged
]

# to track when s-t-o-p is requested
pots = False

#####################################################################################################
# F U N C T I O N S

# Cleanup temp files
def clean_exit(signum=None, frame=None):
    global pots
    pots = True
    print("Cleaning up and exiting...")
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
    sys.exit(1)

def fix_double_quotes(text):
    # First pattern: ([a-zA-Z])("")
    text = re.sub(r'([a-zA-Z])("")', r'\1"', text)
    # Second pattern: ("")([a-zA-Z])
    text = re.sub(r'("")([a-zA-Z])', r'"\2', text)
    return text

# convert double_quotes to single in a file
def replace_double_quotes_patterns(file_path):
    temp_file_path = file_path + ".tmp"
    
    with open(file_path, "r", encoding="utf-8") as infile, open(temp_file_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            modified_line = fix_double_quotes(line)
            outfile.write(modified_line)

    os.replace(temp_file_path, file_path)  # Replace original file with the modified version


# Ask the user to import a file
def ask_for_file(title="Select a file"):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])
    # If no file selected
    if not file_path:
        clean_exit()
    return file_path

# Replace semicolons with commas in a file
def replace_semicolons_with_commas(file_path):
    temp_file_path = file_path + ".tmp"  # Temporary file to hold modified content
    with open(file_path, "r", encoding="utf-8") as infile, open(temp_file_path, "w", encoding="utf-8") as outfile:
        for line in infile:
            modified_line = line.replace(";", ",")  # Replace semicolons with commas
            outfile.write(modified_line)
    os.replace(temp_file_path, file_path)  # Replace the original file with the modified one

# Extract and save hostnames from output file
def extract_and_save_hostnames(output_file, new_file):
    pattern = r"[a-zA-Z]{3,5}_[a-zA-Z0-9]{4,6}_[0-9]{1,3}"
    hostnames = set()  # to ensure uniqueness
    with open(output_file, "r", encoding="utf-8") as infile:
        for line in infile:
            match = re.search(pattern, line)
            if match:
                hostnames.add(match.group(0))  # Add to set to avoid duplicates
    # Write the unique hostnames to a new file
    with open(new_file, "w", newline="", encoding="utf-8") as outfile:
        for hostname in hostnames:
            outfile.write(hostname + "\n")
    print(f"Hostnames Extracted!")

# Decode from Base64
def decode_from_base64(encoded_string):
    return base64.b64decode(encoded_string.encode("utf-8")).decode("utf-8")

# Ask user for the remote device type
def select_group(Group1,Group2):
    inval_inpt = False #um doppelte Fehlermeldungen (in Else-Teil der Loop) zu vermeiden
    print("\nWähle den gewünschten Speichertyp, auf dem der Befehl ausgeführt werden soll:")
    print("o Press 'p' for HPE-Primera A650")
    print("o Press '3' for HPE-3PAR 8200 and 8450")
    while True:
        event = keyboard.read_event()  # Waits for a key press
        if event.event_type == keyboard.KEY_DOWN:  # Ensure it captures only key down events
            key = event.name.lower()

            if key == "p":
                return Group1, "Primera"
            elif key == "3":
                return Group2, "3PAR"
            else:
                print("\nUngültige Auswahl!!")

        time.sleep(0.1)  # CPU load

# um die Spalten, die ihre erste Zelle auch ähnliche Inhalte wie X,Y hat, zu finden.
def find_matching_column(headers, keywords):
    for header in headers:
        normalized_header = header.strip().lower()  # Normalize whitespace and case
        if any(re.search(rf'\b{keyword.lower()}\b', normalized_header) for keyword in keywords):
            return header  # Return the first matching column name
    return None  # No match found

#------------------------------------------------------------#

# Extract and save matching lines from the imported file
def find_host_from_sannav(imported_file, new_output_file, result_file):
    replace_semicolons_with_commas(imported_file)
    replace_double_quotes_patterns(imported_file)
    # Read the lines from the new_output_file (hostnames) into a list
    with open(new_output_file, "r", encoding="utf-8") as f:
        existing_lines = [line.strip() for line in f.readlines()]

    matches = []

    # Read the imported file and search for matches
    with open(imported_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)  # Use DictReader for easier column access

        # Check if the necessary columns exist in the header
        if "Host" not in reader.fieldnames or "Node Symbolic Name" not in reader.fieldnames:
            print("Error: Imported file must have 'Host' and 'Node Symbolic Name' columns.")
            return

        for row in reader:
            # Ignore rows where 'Host' is empty or 'Zone Alias' contains '_r'
            if not row["Host"] or "_r" in row.get("Zone Alias", ""):
                continue

            # Check if any of the columns in the current row match any hostname from new_output_file
            for line in existing_lines:
                # Iterate through every column in the row
                for column in row:
                    if line in row[column]:  # Match if any column contains the hostname
                        # If a match is found, add the 'Host' and 'Node Symbolic Name' columns to the matches list
                        matches.append({"Host": row["Host"], "Node Symbolic Name": row["Node Symbolic Name"]})
                        break  # Stop checking after the first match is found

    # Save the matches to a new CSV file with semicolons
    with open(result_file, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = ["Host", "Node Symbolic Name"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")  # Use semicolons as delimiter
        writer.writeheader()
        writer.writerows(matches)

    print(f"mergaed all Hostnames!")

#------------------------------------------------------------#

# Clean and transform the Symbolic_Name
def Node_Symbolic_Name_Analyse(file_path, result_file):
    with open(file_path, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter=";")
        rows = list(reader)

    if not rows or len(rows[0]) < 2:
        print("Error: The imported file must have at least two columns.")
        return

    transformed_rows = [["Host", "HBA Model", "Firmware", "Driver", "OS"]]  # Header row
    for row in rows[1:]:
        host = re.sub(r"\..*", "", row[0])  # Remove everything after the first dot in the 'Host' column
        hba_model = row[1]
        firmware = driver = os_info = ""

        # Remove content between [] and quotes
        hba_model = re.sub(r"\[.*?\]|\"", "", hba_model)

        # Remove words matching the pattern [a-z]{4}-[0-9]{4,5}-[0-9]{2,3}
        hba_model = re.sub(r"[A-Za-z]{4}-[0-9]{4,6}-[0-9]{2,4}", "", hba_model).strip()

        # Handle 'FCoE' case
        fcoe_match = re.search(r"FCoE\s+(\S+)\s+(\S+)", hba_model)
        if fcoe_match:
            firmware = fcoe_match.group(1)
            driver = fcoe_match.group(2)
            hba_model = re.sub(r"FCoE\s+\S+\s+\S+", "FCoE", hba_model).strip()

        # Handle 'over' case
        over_match = re.search(r"(\S+)\s+over\s+(\S+)", hba_model)
        if over_match:
            firmware = over_match.group(1)
            driver = f"over {over_match.group(2)}"
            hba_model = re.sub(r"\S+\s+over\s+\S+", "", hba_model).strip()

        # Extract and move 'OS:' and everything after it to the OS column
        os_match = re.search(r"OS:.*", hba_model)
        if os_match:
            os_info = re.sub(r"OS:", "", os_match.group(0)).strip()
            hba_model = re.sub(r"OS:.*", "", hba_model).strip()

        # Extract and move other patterns
        elements = hba_model.split()
        remaining_hba_model = []

        for element in elements:
            if element.startswith("FW:"):
                firmware = element[3:]
            elif element.startswith("DVR:"):
                driver = element[4:]
            elif re.match(r"vx\.\d+", element):
                if not firmware:
                    firmware = element
                elif not driver:
                    driver = element
            elif element.startswith("DV"):  # Move words starting with 'DV' to the Driver column
                if not driver:
                    driver = element
            elif element.startswith("FV"):  # Keep the 'FV' logic unchanged
                if not firmware:
                    firmware = element
            elif re.match(r"(VMware|Window|Citrix|Linux|ESX)", element) and not os_info:
                os_info += " " + element.strip()
            else:
                remaining_hba_model.append(element)

        # Handle two 'vx.*' cases
        vx_matches = re.findall(r"(vx\.\d+)", " ".join(remaining_hba_model))
        if len(vx_matches) >= 2:
            firmware = vx_matches[0]
            driver = vx_matches[1]

        # Clean up the HBA model
        hba_model_cleaned = " ".join(remaining_hba_model)
        hba_model_cleaned = re.sub(r"(Emulex|QLogic|HN:\S+)", "", hba_model_cleaned).strip()

        # Append the transformed row
        transformed_rows.append([
            host,
            hba_model_cleaned,
            firmware,
            driver,
            os_info.strip()
        ])

    # Save the transformed data to the result file
    with open(result_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter=";")
        writer.writerows(transformed_rows)

    print(f"Node_Symbolic_Name has been analyzed!")

#------------------------------------------------------------#

# Extract and Add OS from cmdb to the output
def update_os_column(main_file, os_file, result_file):
    replace_semicolons_with_commas(os_file)
    replace_double_quotes_patterns(os_file)
    # Load the OS information into a dictionary for quick lookup
    os_mapping = {}
    with open(os_file, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            
            # Find actual column names dynamically
            bezeichnung_col = find_matching_column(reader.fieldnames, ["Bezeichnung", "Title"])
            betriebssystem_col = find_matching_column(reader.fieldnames, ["Betriebssystem", "Operating system"])

            if not bezeichnung_col or not betriebssystem_col:
                print("Error: The OS file must have 'Bezeichnung/Title' and 'Betriebssystem/Operating system' columns.")
                return

            for row in reader:
                key = (row.get(bezeichnung_col) or "").strip().lower()  # Normalize key
                value = (row.get(betriebssystem_col) or "").strip()  # Avoid NoneType error
                if key and value:  # Only add if both key and value exist
                    os_mapping[key] = value

    # Update the main file with OS information
    with open(main_file, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter=";")
        rows = list(reader)

    updated_rows = [rows[0]]  # Keep the header row
    missing_os = []  # List to keep track of missing OS entries

    for row in rows[1:]:
        if len(row) < 5:
            row.append("")  # Ensure there is an OS column
        host = row[0].strip().lower()  # Normalize host to lowercase
        os_info = os_mapping.get(host, "")

        if not os_info:
            missing_os.append(host)  # Log missing OS entries
        row[4] = os_info  # Update the OS column
        updated_rows.append(row)

    # Save the updated data to the result file
    with open(result_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter=";")
        writer.writerows(updated_rows)
    
    print(f"OS is added!")

    # Log missing OS entries
    if missing_os:
        print(f"OS information is missing for the Hosts: {' and '.join(missing_os)}")

#####################################################################################################
# Signal handler for cleanup [CTRL+C]

signal.signal(signal.SIGINT, clean_exit)
signal.signal(signal.SIGTERM, clean_exit)

#####################################################################################################
# Removal previous temps in case there's any

for file in temp_files:
    if os.path.exists(file):
        os.remove(file)

#####################################################################################################
# Checkings:

# Ensure temp directory exists
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
    print(f"Created: {temp_dir}")

#####################################################################################################
# etl@te karb@ri

enP = "UH90JbTE0gw"
enC = "c2hvd2hvc3Q="
enU = "MFfgjyhdbQ="
com1 = decode_from_base64(enC)
ucred = decode_from_base64(enU)
pcred = decode_from_base64(enP)

#####################################################################################################
# Connection 2 Speicher

Prm = [
	{"hname": "10.10.10.67", "karbar": ucred, "amn": pcred,},
	{"hname": "10.10.10.78", "karbar": ucred, "amn": pcred},
]

dPar = [
	{"hname": "10.10.10.35", "karbar": ucred, "amn": pcred,},
	{"hname": "10.10.10.34", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.39", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.20", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.14", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.3", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.5", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.6", "karbar": ucred, "amn": pcred,},
    {"hname": "10.10.10.2", "karbar": ucred, "amn": pcred},
]

# ask about the Device type
devices,ty = select_group(Prm,dPar)
FNL = os.path.join(m_drve, f"HostWorkSheet_{ty}_{today_date}.csv")

# Connect and extract Hostnames
try:
    with open(output_raw, "a") as output_file:
        for device in devices:
            h1 = device["hname"]
            u1 = device["karbar"]
            p1 = device["amn"]
            if pots:
                print("Stopped 0")
                clean_exit()
                sys.exit(1)
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=h1, port=22, username=u1, password=p1)
                print(f"Querying {h1}...")

                stdin, stdout, stderr = ssh.exec_command(com1)
                output = stdout.read().decode("utf-8")
                error = stderr.read().decode("utf-8")

                if error:
                    print(f"Error on {h1}: {error}")
                else:
                    for line in output.splitlines():
                        if "Name" in line or "total" in line or "--" in line:
                            continue
                        columns = line.split()
                        if len(columns) >= 2:
                            second_column = re.sub(r'\d+:\d+:\d+', '', columns[1].strip())
                            if second_column:
                                output_file.write(second_column + "\n")
                                if pots:
                                    print("Stopped 1")
                                    sys.exit(1)
                    print(f"Filtered and saved!")
                ssh.close()
            
            except Exception as e:
                print(f"An error occurred with {h1}: {e}")
                #sys.exit(1)
except Exception as e:
    print(f"An error occurred while opening the file or processing: {e}")
    clean_exit()
    sys.exit(1)  # Exit if an error occurs at the file opening or main loop level

# Mark the output file as hidden
subprocess.run(["attrib", "+h", output_raw], shell=True)

# Extract the exact Hostnames and save to a new file
extract_and_save_hostnames(output_raw, laniF)
# clean the past 1 & h it
subprocess.run(["attrib", "+h", laniF], shell=True)
if os.path.exists(output_raw):
    os.remove(output_raw)

#####################################################################################################
# Import and integrate the SANnav-Report

SANnav = ask_for_file('Import the Host-Port Report from SANnav ...')
find_host_from_sannav(SANnav, laniF, merged)

# clean the past 2
if os.path.exists(laniF):
    os.remove(laniF)

# hidding
subprocess.run(["attrib", "+h", merged], shell=True)

# Add HBA-Model, Firmware and Driver
Node_Symbolic_Name_Analyse(merged, tilOS)
subprocess.run(["attrib", "+h", tilOS], shell=True)

# clean the past 3
if os.path.exists(merged):
    os.remove(merged)

#####################################################################################################
# Import and integrate die physischen Server-Liste

os_file_path = ask_for_file('Import the Server List from CMDB ...')
update_os_column(tilOS, os_file_path, FNL)
# clean the past 3
if os.path.exists(tilOS):
    os.remove(tilOS)