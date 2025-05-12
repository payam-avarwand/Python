# This script export all VBA codes of a VBA macro file into cls files.

# created:      Payam Avarwand - 05.03.2025
# last change:  Payam Avarwand - 06.03.2025

################# import_Libs #################
import sys
import subprocess
import importlib.util

#####################################################################################################
# Lib-Check and import

LbsS = [
    "chardet",
    "tkinter",
    "re",
    "xlwings",
    "os",
    "time",
    "psutil"
]

def check_and_install_libraries():
    for lib in LbsS:
        if importlib.util.find_spec(lib) is None:
            print(f"Installing {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

        globals()[lib] = importlib.import_module(lib)
#------------------------------------------------------------#

check_and_install_libraries()
import chardet
from tkinter import filedialog, Tk
import re
import os
import xlwings as xw
import psutil
import time

#####################################################################################################
# F u n c t i o n s

def is_excel_running():
    """Check if Excel is running."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'].lower() == 'excel.exe':
            return True
    return False

def kill_excel():
    """Terminates all running Excel processes if they exist."""
    if is_excel_running():
        try:
            subprocess.run(["taskkill", "/IM", "excel.exe", "/F"], check=True, shell=True)
            print("All Excel processes have been closed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to close Excel: {e}")
    else:
        print("No Excel file is open.")

def save_vba_code(sheet_code, output_folder, sheet_name):
    """Saves VBA code into a .cls file inside the specified output folder."""
    clean_name = sheet_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    output_file = os.path.join(output_folder, f"{clean_name}.cls")

    try:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(sheet_code)
        print(f"VBA code for {sheet_name} saved to {output_file}")
    except Exception as e:
        print(f"Error saving VBA code for {sheet_name}: {e}")

def extract_vba_from_sheets():
    """Extracts VBA code from an Excel .xlsm file and saves it to a corresponding folder."""
    root = Tk()
    root.withdraw()  # Hide the root Wndw

    input_file = filedialog.askopenfilename(
        title="Please select the VBA-Macro File ...",
        filetypes=(("Excel Files", "*.xlsm"), ("All Files", "*.*"))
    )

    if not input_file:
        print("No input file selected.")
        return

    file_name = os.path.splitext(os.path.basename(input_file))[0]

    output_parent_folder = filedialog.askdirectory(
        title="Please select an Output Path ..."
    )

    if not output_parent_folder:
        print("No output folder selected. Extraction was not performed.")
        return

    output_folder = os.path.join(output_parent_folder, file_name)
    os.makedirs(output_folder, exist_ok=True)

    app = xw.App(visible=False)  
    app.api.AutomationSecurity = 3  # Disable macros
    wb = app.books.open(input_file)

    time.sleep(2)

    for component in wb.api.VBProject.VBComponents:
        try:
            if component.Type in [1, 2, 100]:  # Modules, Class Modules, Worksheets/ThisWorkbook
                sheet_code = component.CodeModule.Lines(1, component.CodeModule.CountOfLines) if component.CodeModule.CountOfLines > 0 else ""
                save_vba_code(sheet_code, output_folder, component.Name)
        except Exception as e:
            print(f"Error extracting VBA from {component.Name}: {e}")

    print("VBA extraction complete!")
    wb.close()
    app.quit()

kill_excel()

if __name__ == "__main__":
    extract_vba_from_sheets()
