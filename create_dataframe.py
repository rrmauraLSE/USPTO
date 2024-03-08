
"""
This creates a dataframe by parsing XML files in a given folder. 
The XML files contain information about patent publications, including: 
- publication title
- number
- date
- application type
- classifications
- inventors
- abstracts
- descriptions
- claims

The script unzips any compressed files in the folder and its subfolders, 
then parses each XML file to extract the relevant information. 
The extracted information is stored in a pandas DataFrame, saved as a CSV file.
"""

import os
import zipfile
import html
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

# Notes for me:
# it takes around 10 min to run for 2 folders.
# the csv file is 500MB approximately.

# TODO: what am I supossed to do with the supplementary material?
# TODO: delete the zip files after unzipping them
# TODO: when you do the whole thing, add a "try", and keep track of the files that failed to parse


def is_file_compressed(file_path: str) -> bool:
    """
    Checks if a file is compressed (zip or tar).

    Args:
        file_path (str): The path of the file.

    Returns:
        bool: True if the file is compressed, False otherwise.
    """
    lowercase_path = file_path.lower()
    return lowercase_path.endswith(".zip") or lowercase_path.endswith(".tar")


def unzip_files(folder: str) -> None:
    """
    Unzips all files in the folder and subfolders.

    Args:
        folder (str): The path of the folder.
    """
    for root, dirs, files in os.walk(folder):
        for file in tqdm(files, desc="Unzipping files"):
            if is_file_compressed(file):
                # check first if they have been already unzipped
                if not os.path.exists(os.path.join(root, file[:-4])):
                    tqdm.write(f"Unzipping {file}...")
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                        zip_ref.extractall(root)
                    tqdm.write(f"Unzipped {file}")
                else:
                    tqdm.write(f"File {file} already unzipped, skipping.")

                # unzip all zip files within the unzipped folder
                unzip_files(os.path.join(root, file[:-4]))


def parse_xml(xml_path: str) -> dict:
    """
    Parses an XML file and extracts relevant information.

    Args:
        xml_path (str): The path of the XML file.

    Returns:
        dict: A dictionary containing the extracted information.
    """

    def get_text_or_none(tag):
        return tag.get_text() if tag else None

    with open(xml_path, 'r', encoding='UTF-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')

    # Extracting publication title, number, and date
    title = get_text_or_none(soup.find('invention-title'))
    number = get_text_or_none(
        soup.find('publication-reference').find('doc-number'))
    date = get_text_or_none(soup.find('publication-reference').find('date'))

    # Application type
    application_reference = soup.find('application-reference')
    application_type = application_reference['appl-type'] if application_reference else None

    # Classifications
    ipc_classifications = [get_text_or_none(
        ipc) for ipc in soup.find_all('classification-ipc')]
    national_classifications = [get_text_or_none(
        nc) for nc in soup.find_all('classification-national')]

    # Inventors
    inventors = [{'last_name': get_text_or_none(inventor.find('last-name')),
                  'first_name': get_text_or_none(inventor.find('first-name'))}
                 for inventor in soup.find_all('applicant')]

    # Abstract
    abstract = get_text_or_none(soup.find('abstract'))

    # Description
    description = get_text_or_none(soup.find('description'))

    # Claims
    claims = [claim.get_text(separator="\n", strip=True)
              for claim in soup.find_all('claim')]

    return {
        'publication_title': title,
        'publication_number': number,
        'publication_date': date,
        'application_type': application_type,
        'ipc_classifications': ipc_classifications,
        'national_classifications': national_classifications,
        'inventors': inventors,
        'abstract': abstract,
        'description': description,
        'claims': claims
    }


def create_dataframe(folder_year: str) -> pd.DataFrame:
    """
    Creates a dataframe by parsing XML files in a given folder.

    Args:
        folder_year (str): The path of the folder containing the XML files.

    Returns:
        pd.DataFrame: The created dataframe.
    """
    # create empty dataframe
    df = pd.DataFrame(columns=['publication_title',
                               'publication_num',
                               'publication_date',
                               'application_type',
                               'classifications',
                               'inventors',
                               'abstract',
                               'descriptions',
                               'claims'])

    # iterate over all XML files in the folder
    all_xml_files = []
    for root, _, files in os.walk(folder_year):
        for file in files:
            if file.lower().endswith(".xml"):
                xml_path = os.path.join(root, file)
                all_xml_files.append(xml_path)

    for xml_path in tqdm(all_xml_files, desc="Parsing XML files"):
        parsed_xml = parse_xml(xml_path)
        df = pd.concat([df, pd.DataFrame([parsed_xml])],
                       ignore_index=True)

        # TODO: add image embeddings and text embeddings

    return df


if __name__ == "__main__":

    # main_folder = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\images_and_text_data"

    # folder_year = os.path.join(main_folder, "2005")

    # fake folder to do testing:
    folder_year = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\fake_2005_folder"

    # unzip_files(folder_year)

    df = create_dataframe(folder_year)

    print("Dataframe created")

    # save dataframe to csv
    df.to_csv(os.path.join(folder_year, "dataframe.csv"), index=False)

    # TODO: run this on a notebook and check the dataframe, and how big it is.
