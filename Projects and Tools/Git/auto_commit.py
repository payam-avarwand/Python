# This Script will automate the committing of changes to a Git Repository.

# created:      Payam Avarwand - 10.01.2025
# last change:  Payam Avarwand - 03.06.2025

################# import_Libs #################
import os
import subprocess
from datetime import datetime

################# Git Process:
# Set the path to the Repository
repo_path = "D:\\Interface-Track"

# Navigate to Repo
os.chdir(repo_path)

# Add Changes
subprocess.run(["git", "add", "."], check=True)

# Commit
commit_message = f"Auto-commit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
subprocess.run(["git", "commit", "-m", commit_message], check=True)

################# Output message #################
print("Changes committed.")
