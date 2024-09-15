''' This provides a merged list of our local LUN-List and all LUN-Lists from every single Storage-System,
    and then will create a Log file to inform about the LUNs that have more than one Record in our local-List.
    '''

# Prerequisites:
    # - all Input files (Lists) must be csv data.
    # - we will have to copy all Input files in "D:\LUN\". [we can change the drive letter in the variable definition part]
    # - the name of all LUN-Lists from every single Storage-System must start with "bess-" or "wuss-".
    # - the whole name of the local LUN-List must be> "cmdb-lun.csv"
    

# created:      Payam Avarwand - 21.08.2024
# last change:  Payam Avarwand - 23.08.2024

################# import_Libs #################
import csv
import shutil
import os
import subprocess
import sys
import re
import chardet


################# install Panda-package:
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check if pandas is installed:
try:
    import pandas as pd
except ImportError:
    print("Pandas not found. Installing pandas...")
    install('pandas')
    import pandas as pd



################# design and define functions #################

################# mix the cmdb-output-list with all storage-output-lists
def fill_WWN_from_storage_output(Storage, cleanCMDBList, output_file):
    """
    Fills 'second column' values in the file 'cleanCMDBList' based on corresponding 'second column' values from 'Storage'.
    """

    # Create a mapping between 'cl1' and 'cl2' from Storage
    cl1_to_cl2 = {}

    with open(Storage, 'r') as f1:
        reader = csv.reader(f1)
        next(reader)  # Skip header
        for row in reader:
            cl1_to_cl2[row[0]] = row[1]

    # Open cleanCMDBList, fill in the missing 'cl2' values, and write to output_file
    with open(cleanCMDBList, 'r') as f2, open(output_file, 'w', newline='') as output:
        reader = csv.reader(f2)
        writer = csv.writer(output)

        # Write the header
        header = next(reader)
        writer.writerow(header)

        # Process each row in cleanCMDBList
        for row in reader:
            if not row[1]:  # If 'cl2' is empty
                row[1] = cl1_to_cl2.get(row[0], '')  # Fill with corresponding 'cl2' value from Storage
            writer.writerow(row)
            


################# remove duplicated lines
# the same Lun names with the same WWNs on the same Storage-System could be removed, this duplications are just because of Zoning-mechanism
def remove_duplicates(file1, Storage):
    unique_rows = set()
    with open(file1, 'r') as infile, open(Storage, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)  # Read the header
        writer.writerow(header)  # Write the header to the output file

        for row in reader:
            row_tuple = tuple(row)  # Convert row to a tuple to store in a set (since lists can't be added to sets)
            if row_tuple not in unique_rows:
                unique_rows.add(row_tuple)
                writer.writerow(row)  # Write the row to the output file only if it's unique




################# define Variables #################

path0="D:\\"
path1 = "D:\\Storages_2024_1_Temp\\"
src_path = "D:\\LUN"

################# Get all LUN-lists

Storages = {}
files = os.listdir(src_path)

# Get all files that start with 'bess-' or 'wuss-' and end with '.csv' as members in the dictionary
for k, filename in enumerate(sorted([f for f in files if (f.startswith('bess-') or f.startswith('wuss-')) and f.endswith('.csv')]), start=1):
    Storages[k] = filename

list_amount = len(Storages)




################# Check the temp path and use the Lists 
if os.path.exists(path1):
    # If directory exists, delete the contents
    shutil.rmtree(path1)

shutil.copytree(src_path, path1)



################# Clean the csv-List of cmdb #################

################# replace  to none (remove that)
input_file1 = path1+"cmdb-lun.csv"
output_file1 = path1+"LUNs1.csv"

# Read the content of the input file, replace commas with semicolons, and write to the output file
with open(input_file1, 'r') as infile:
    content = infile.read()
    modified_content = content.replace('', '')

# Write the modified content to the output file
with open(output_file1, 'w') as outfile:
    outfile.write(modified_content)

del (input_file1)
del (output_file1)


################# replace ; to ,
input_file2 = path1+"LUNs1.csv"
output_file2 = path1+"LUNs2.csv"

with open(input_file2, 'r') as infile:
    content = infile.read()
    modified_content = content.replace(';', ',')

with open(output_file2, 'w') as outfile:
    outfile.write(modified_content)
print(f"semicolons have been replaced with Commas in {output_file2}.")

os.remove(input_file2)
del (input_file2)
del (output_file2)


################# Reading the CSV file with error handling
input_file3 = path1+"LUNs2.csv"
output_file3 = path1+"LUNs.csv"

try:
    df = pd.read_csv(input_file3, on_bad_lines='warn')  # Warn about problematic lines
except pd.errors.ParserError as e:
    print(f"Error parsing {input_file3}: {e}")
    sys.exit(1)  # Exit the script if parsing fails

# Ensure that all columns are correctly aligned by filling missing values
df = df.fillna('')  # Fill missing values with empty strings

# Handle potential issues with the number of columns
expected_columns = ['Bezeichnung', 'WWN/UID', 'ID', 'Größe in GB', 'Storage System']
if set(expected_columns).issubset(df.columns):
    df = df[expected_columns]  # Reorder columns
else:
    print(f"Missing expected columns in {input_file3}. Please check the CSV file.")
    sys.exit(1)

# Rename the columns
df.columns = ['LUN Name', 'WWN', 'ID', 'Size (GB)', 'Storage System']

# Save the cleaned and reordered DataFrame to a new CSV file
df.to_csv(output_file3, index=False)


os.remove(input_file3)
del input_file3
del output_file3


cleanCMDBList = path1+"LUNs.csv"
output_file = path1+"autput.csv"

i=1
for i in range (1,list_amount+1,1):
    HPE_RAW_list = path1+Storages[i]
    Storage_File= path0+"temp"+ str(i)+'.csv'
    remove_duplicates(HPE_RAW_list, Storage_File)
    fill_WWN_from_storage_output(Storage_File, cleanCMDBList, output_file)
    cleanCMDBList = path1+'new_file.csv'
    shutil.copyfile(output_file, cleanCMDBList)
    os.remove(Storage_File)
    os.remove(output_file)

os.remove(path1+"LUNs.csv")



################# Prepare the LUN List to check and find the duplicated ones #################
input_file4 = path1+"new_file.csv"
output_file5=path0+"LUN_Name-with-WWN.csv"


################# Reading the CSV file with error handling
try:
    df = pd.read_csv(input_file4, on_bad_lines='warn')  # Warn about problematic lines
except pd.errors.ParserError as e:
    print(f"Error parsing {input_file4}: {e}")
    sys.exit(1)  # Exit the script if parsing fails

################# Ensure that all columns are correctly aligned by filling missing values
df = df.fillna('')  # Fill missing values with empty strings


################# Handle potential issues with the number of columns
expected_columns = ['LUN Name', 'WWN']
if set(expected_columns).issubset(df.columns):
    df = df[expected_columns]  # Reorder columns
else:
    print(f"Missing expected columns in {input_file4}. Please check the CSV file.")
    sys.exit(1)


################# Rename the columns
df.columns = ['LUN Name', 'WWN']

################# Save the cleaned and reordered DataFrame to a new CSV file
df.to_csv(output_file5, index=False)



################# log the LUNs with more than one record on all Storages #################
################# PowerShell command as an f-string to correctly concatenate Python variables
powershell_command1 = rf'Get-Content "{path0}LUN_Name-with-WWN.csv" | Group-Object | Where-Object {{ $_.Count -gt 1 }} | Sort-Object Count -Descending | Format-Table Name, Count -AutoSize -Wrap > "{path0}LUN-Log-0.txt"'

################# Run PowerShell command from Python
subprocess.run(["powershell.exe", "-Command", powershell_command1], check=True)

# Hint: the Output txt data of Powershell, has not the normal encoding like 'utf-8', so it must be checked!


################# Change the Log Order:

# Define the file paths
RAW_LOG1 = path0+"LUN-Log-0.txt"  # The source file
output_log = path0+"LUN-Log.txt"  # The transformed output file

# Detect the encoding of the source file
with open(RAW_LOG1, 'rb') as infile:
    raw_data = infile.read()
    encoding = chardet.detect(raw_data)['encoding']
    print("")
    print(f"Encoding of the PowerShell-Log is: {encoding}")

# Read and process the file contents
with open(RAW_LOG1, 'r', encoding=encoding) as infile:
    lines = infile.readlines()

# Regular expression pattern to match the Name and Count parts
pattern = re.compile(r'(.+)\s+(\d+)$')

# Open the output file and write the transformed data
with open(output_log, 'w', encoding='utf-8') as outfile:
    # Write the header for the output file
    outfile.write('Count\tName\n')
    outfile.write('-----\t-----\n')
    
# Process each line after the header (skipping first two lines)
    for line in lines[2:]:
        match = pattern.match(line.strip())
        if match:
            name, count = match.groups()  # Extract name and count
            # Format the name with " | " separator
            formatted_name = f"{name[:name.rfind(',')]} | {name[name.rfind(',')+1:]}"
            outfile.write(f'{count} : {formatted_name}\n')

# Clean up the original file if necessary
os.remove(RAW_LOG1)
print("\nLog-File transformation completed!")



################# Replace Semicolon to Comma in the output LUN-List
Last_input_file = input_file4
Last_output_file = path0+"LUN-LIST.csv"

with open(Last_input_file, 'r') as infile:
    content = infile.read()
    modified_content = content.replace(';', ',')

with open(Last_output_file, 'w') as outfile:
    outfile.write(modified_content)
    print("")
    print(f"Commas have been replaced with semicolons in {Last_output_file}.")

os.remove(Last_input_file)
os.remove(output_file5)
shutil.rmtree(path1)
