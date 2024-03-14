
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

from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import html
import zipfile
import os
import tiktoken


MAX_CALLS_PER_SECOND = 10
TXT_COLUMNS = ["abstract", "claims", "description", "title"]
MODEL = "text-embedding-ada-002"
MAX_TOKENS = 8191  # this value depends on the model.

# Notes for me:
# it takes around 10 min to run for 2 folders.
# the csv file is 500MB approximately.

# TODO: what am I supossed to do with the supplementary material?
# TODO: delete the zip files after unzipping them


def count_tokens(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


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
        # save the name of the tag
        return tag.get_text() if tag else None

    with open(xml_path, 'r', encoding='UTF-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')

    # Extracting publication title, number, and date
    title = soup.find('invention-title').get_text()
    number = soup.find('publication-reference').find('doc-number').get_text()
    date = soup.find('publication-reference').find('date').get_text()

    # Application type
    application_reference = soup.find('application-reference')
    application_type = application_reference['appl-type'] if application_reference else None

    # Classifications
    ipc_classifications = [ipc.get_text()
                           for ipc in soup.find_all('classification-ipc')]
    national_classifications = [nc.get_text()
                                for nc in soup.find_all('classification-national')]

    # Inventors
    inventors = [{'last_name': inventor.find('last-name').get_text(),
                  'first_name': inventor.find('first-name').get_text()}
                 for inventor in soup.find_all('applicant')]

    # Abstract
    abstract = soup.find('abstract').get_text()

    # Description
    description = soup.find('description').get_text()

    # Claims
    claims = [claim.get_text(separator="\n", strip=True)
              for claim in soup.find_all('claim')]

    return {
        'title': title,
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


def get_relevant_xml_files(folder: str) -> list:
    all_xml_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            # ignore SEQLST files (they contain genetic list data)
            if file.lower().endswith(".xml") and "seqlst" not in file.lower():
                xml_path = os.path.join(root, file)
                all_xml_files.append(xml_path)
    return all_xml_files


def create_dataframe(folder_year: str) -> pd.DataFrame:
    """
    Creates a dataframe by parsing XML files in a given folder.

    Args:
        folder_year (str): The path of the folder containing the XML files.

    Returns:
        pd.DataFrame: The created dataframe.
    """
    # create empty dataframe
    df = pd.DataFrame(columns=['title',
                               'publication_number',
                               'publication_date',
                               'application_type',
                               'ipc_classifications',
                               'national_classifications',
                               'inventors',
                               'abstract',
                               'description',
                               'claims'])

    error_files = []

    # iterate over all XML files in the folder
    relevant_xml_files = get_relevant_xml_files(folder_year)

    for xml_path in tqdm(relevant_xml_files, desc="Parsing XML files"):
        try:
            parsed_xml = parse_xml(xml_path)
            df = pd.concat([df, pd.DataFrame([parsed_xml])],
                           ignore_index=True)

        except Exception as e:
            print(f"Error parsing {xml_path}: {e}")
            error_files.append(xml_path)

    return df, error_files


if __name__ == "__main__":

    # main_folder = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\images_and_text_data"

    # folder_year = os.path.join(main_folder, "2005")

    # fake folder to do testing:
    folder_year = r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\fake_2005_folder"

    # unzip_files(folder_year)

    df, error_files = create_dataframe(folder_year)

    # save error files
    with open(os.path.join(folder_year, "error_files.txt"), "w") as file:
        for error_file in error_files:
            file.write(error_file + "\n")

    # count characters and tokens
    for col in TXT_COLUMNS:
        df[f"{col}_characters"] = df[col].apply(lambda x: len(x))
        df[f"{col}_tokens"] = df[col].apply(lambda x: count_tokens(x, MODEL))

    # save dataframe to csv
    df.to_csv(os.path.join(folder_year, "dataframe.csv"), index=False)

    print("Dataframe created")
    print(f"Error files: {len(error_files)}")
