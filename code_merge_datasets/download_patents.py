# obtain USPTO patent examination research dataset from the USPTO website

import requests
import os
import zipfile
import shutil
import time
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the download directory
download_directory = "data"
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Set up the download URL
url = "https://bulkdata.uspto.gov/data/patent/examination/corpus/2018/"

# Set up the file name
filename = "PatentCorpusData"

# Set up the file path
file_path = os.path.join(download_directory, filename)

# Set up the file extension
extension = ".zip"

# Set up the file URL
file_url = url + filename + extension

# Set up the file download path
file_download_path = file_path + extension

# Download the file
logger.info("Downloading the file from: " + file_url)
r = requests.get(file_url)
with open(file_download_path, "wb") as f:
    f.write(r.content)

# Unzip the file
logger.info("Unzipping the file: " + file_download_path)


