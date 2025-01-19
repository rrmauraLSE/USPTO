"""Downloads USPTO patent application ZIP/TAR files from specified years.

This script downloads patent application files from the USPTO data website.
It can download either text-only files or files containing embedded TIFF images
for specified years.

Example:
    To download image files for year 2005:
    >>> year = "2005"
    >>> text_or_image = "image"
    >>> application_or_grant = "application"
    >>> download_zip_files(year, text_or_image, application_or_grant)
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Literal

# Configure download parameters
FIRST_YEAR = 2005
FINAL_YEAR = 2005


def download_zip_files(
    year: str,
    text_or_image: Literal["text", "image"],
    application_or_grant: Literal["application", "grant"] = "application"
) -> None:
    """Downloads USPTO patent ZIP/TAR files for a specific year and type.

    Args:
        year: The year to download data for.
        text_or_image: Whether to download text-only files or files with images.
        application_or_grant: Whether to download application or grant files.
            Defaults to "application".

    Raises:
        ValueError: If text_or_image is not "text" or "image".
        requests.exceptions.RequestException: If download fails.
    """
    print(f"Downloading {application_or_grant} files ({text_or_image})")

    # Construct base URL based on file type
    if text_or_image == "text":
        base_url = (
            f"https://bulkdata.uspto.gov/data/patent/{application_or_grant}"
            f"/redbook/fulltext/{year}/"
        )
    elif text_or_image == "image":
        base_url = (
            f"https://bulkdata.uspto.gov/data/patent/{application_or_grant}"
            f"/redbook/{year}/"
        )
    else:
        raise ValueError('text_or_image must be "text" or "image"')

    # Get directory listing
    response = requests.get(base_url)
    print(f"Accessing {base_url}...")

    if not response.ok:
        print(f"Failed to access {base_url}")
        return

    # Parse directory listing for ZIP/TAR files
    soup = BeautifulSoup(response.text, "html.parser")
    zip_tar_links = [
        urljoin(base_url, link.get("href"))
        for link in soup.find_all("a")
        if link.get("href", "").lower().endswith((".zip", ".tar"))
    ]

    # Create download directory
    base_folder = (
        "C:/Users/Roberto/Documents/GitHub Repositories/USPTO/data/"
        "images_and_text_data"
    )
    folder_path = os.path.join(base_folder, year)
    os.makedirs(folder_path, exist_ok=True)

    # Download each file
    for zip_link in zip_tar_links:
        filename = os.path.join(folder_path, os.path.basename(zip_link))

        if os.path.exists(filename):
            print(f"File {filename} already exists, skipping download.")
            continue

        try:
            print(f"Downloading {filename}...")
            with requests.get(zip_link, stream=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Successfully downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {filename}: {str(e)}")


def main() -> None:
    """Main entry point for the script."""
    for year in range(FIRST_YEAR, FINAL_YEAR + 1):
        download_zip_files(str(year), "image")
    print("Download process completed.")


if __name__ == "__main__":
    main()
