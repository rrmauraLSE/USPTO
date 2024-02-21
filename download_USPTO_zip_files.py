import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os


def download_zip_files(year, text_or_image, application_or_grant="application"):
    print(
        f"YOU ARE DOWNLOADING {application_or_grant} FILES. {text_or_image} ")
    if text_or_image == "text":
        base_url = f"https://bulkdata.uspto.gov/data/patent/{application_or_grant}/redbook/fulltext/{year}/"
        # Patent Application Full Text Data (No Images) (MAR 15, 2001 - PRESENT)
    elif text_or_image == "image":
        base_url = f"https://bulkdata.uspto.gov/data/patent/{application_or_grant}/redbook/{year}/"
        # Patent Application Full Text Data with Embedded TIFF Images (MAR 15, 2001 - PRESENT) (Application Red Book based on WIPO ST.36)
    else:
        raise ValueError("text_or_image must be 'text' or 'image'")

    response = requests.get(base_url)

    print(f"Downloading zip files from {base_url}...")
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')

        # the files can end with .zip, .ZIP, .tar, .TAR
        # TODO: manually confirm you have all files! count them
        zip_tar_links = [
            urljoin(base_url, link.get('href'))
            for link in soup.find_all('a')
            if link.get('href', '').endswith(('.zip', '.ZIP', '.tar', '.TAR'))
        ]

        base_folder = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\images_and_text_data"
        folder_path = os.path.join(base_folder, year)
        os.makedirs(folder_path, exist_ok=True)
        for zip_link in zip_tar_links:
            filename = os.path.join(folder_path, os.path.basename(zip_link))
            if not os.path.exists(filename):
                with requests.get(zip_link, stream=True) as r:
                    r.raise_for_status()
                    with open(filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"Downloaded {filename}")
            else:
                print(f"File {filename} already exists, skipping download.")
    else:
        print(f"Failed to access {base_url}")


first_year = 2005
final_year = 2005

for year in range(first_year, final_year + 1):
    download_zip_files(str(year), "image")
print("Downloaded all zip files")
