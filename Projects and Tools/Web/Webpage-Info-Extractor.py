# This Script will get a Webpage address from User, and gives the RAW Information of the page as output files in D-Drive.

# created:      Payam Avarwand - 25.02.2025
# last change:  Payam Avarwand - 28.02.2025

# Prerequisites:
    # the Firefox Browser must be installed
    # the Firefox-Web driver file [geckodriver.exe] must be in the path:   "C:\selenium\geckodriver.exe"

################# import_Libs #################
import subprocess
import sys
import importlib
import json
import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

# Required libraries (json is built-in and does not need installation)
Libraries = ["selenium"]

###########################################################################################################
# Checkup libraries

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"{package} is not installed. Installing now ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        try:
            importlib.import_module(package)
            print(f"{package} installed successfully.")
        except ImportError:
            sys.exit(f"Error: {package} could not be installed.")

# Install necessary libraries
for lib in Libraries:
    install_and_import(lib)

###########################################################################################################
# GUI Input for Website URL

def get_website_url():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    url = simpledialog.askstring("Website Input", "Enter the website address (e.g., example.com):")
    return url.strip() if url else None

# Get website URL from user
user_input = get_website_url()
if not user_input:
    sys.exit("No URL entered. Exiting...")

# Ensure URL has a scheme (http/https)
parsed_url = urlparse(user_input)
if not parsed_url.scheme:
    user_input = "https://" + user_input  # Default to https

print(f"Accessing: {user_input}")

###########################################################################################################
# Configure Firefox-WebDriver

options = webdriver.FirefoxOptions()
options.headless = True  # Run without GUI

# Firefox preferences for optimization
options.set_preference("browser.cache.disk.enable", False)
options.set_preference("browser.cache.memory.enable", True)
options.set_preference("browser.cache.offline.enable", False)
options.set_preference("network.http.use-cache", False)
options.set_preference("permissions.default.image", 2)  # Disable images
options.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")  # Disable Flash
options.set_preference("browser.display.use_document_fonts", 0)  # Disable web fonts
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
options.set_preference("intl.accept_languages", "en-US, en")  # Set language to English

# GeckoDriver path
service = Service(r"C:\selenium\geckodriver.exe")

# Start WebDriver
driver = webdriver.Firefox(service=service, options=options)

###########################################################################################################
# Open the website

driver.get(user_input)
driver.minimize_window()  # Minimize the browser

###########################################################################################################
# Save HTML source

source_path = r"D:\source.txt"
with open(source_path, "w", encoding="utf-8") as file:
    file.write(driver.page_source)
print(f"HTML source saved in {source_path}.")

###########################################################################################################
# Save page body content

body_path = r"D:\body.txt"
body = driver.find_element(By.TAG_NAME, "body").text
with open(body_path, "w", encoding="utf-8") as file:
    file.write(body)
print(f"Body content saved in {body_path}.")

###########################################################################################################
# Save all links

links = [a.get_attribute("href") for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
link_path = r"D:\Links.txt"
with open(link_path, "w", encoding="utf-8") as file:
    file.write("\n".join(links))
print(f"Links saved in {link_path}.")

###########################################################################################################
# Save image URLs

images = [img.get_attribute("src") for img in driver.find_elements(By.TAG_NAME, "img") if img.get_attribute("src")]
img_path = r"D:\images.txt"
with open(img_path, "w", encoding="utf-8") as file:
    file.write("\n".join(images))
print(f"Images saved in {img_path}.")

###########################################################################################################
# Save meta tags

meta_path = r"D:\meta_tags.txt"
metas = driver.find_elements(By.TAG_NAME, "meta")
with open(meta_path, "w", encoding="utf-8") as file:
    for meta in metas:
        name = meta.get_attribute("name")
        content = meta.get_attribute("content")
        if name and content:
            file.write(f"{name} : {content}\n")
print(f"Meta tags saved in {meta_path}.")

###########################################################################################################
# Save cookies

cookie_path = r"D:\Cookies.json"
cookies = driver.get_cookies()
with open(cookie_path, "w", encoding="utf-8") as file:
    json.dump(cookies, file, indent=4)
print(f"Cookies saved in {cookie_path}.")

###########################################################################################################
# Capture a screenshot

screenshot_path = r"D:\screenshot.png"
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved in {screenshot_path}.")

###########################################################################################################
# Close the browser

driver.quit()
