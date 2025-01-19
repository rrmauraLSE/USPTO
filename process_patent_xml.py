"""Creates a DataFrame from USPTO patent XML files.

This script processes USPTO patent application XML files to extract key
metadata and content including titles, publication details, classifications,
inventors, abstracts, descriptions, and claims. It handles compressed files by
unzipping them first, then parses each XML file to build a DataFrame.

The script follows these main steps:
1. Unzips any compressed files in the target folder and subfolders
2. Identifies relevant XML files (excluding genetic sequence listings)
3. Parses each XML file to extract structured data
4. Builds a DataFrame with the extracted information
5. Calculates text statistics like character and token counts
6. Saves the results to parquet format

Example:
    To process patent files for year 2005:
    >>> folder_year = "path/to/2005/files"
    >>> df, errors = create_dataframe(folder_year)
    >>> df.to_parquet("patents_2005.parquet")
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import tiktoken
import zipfile
import os

# Constants
MAX_CALLS_PER_SECOND = 10
TEXT_COLUMNS = ["abstract", "claims", "description", "title"]
EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_TOKENS = 8191  # Maximum tokens for text-embedding-ada-002 model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = EMBEDDING_MODEL) -> int:
    """Count the number of tokens in a text string using the model's tokenizer.

    Args:
        text: The input text to tokenize
        model: Name of the model whose tokenizer to use

    Returns:
        Number of tokens in the text
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def is_file_compressed(file_path: Path) -> bool:
    """Check if a file is a compressed archive (zip/tar).

    Args:
        file_path: Path to the file to check

    Returns:
        True if file has a compressed format extension
    """
    return file_path.suffix.lower() in {'.zip', '.tar'}


def unzip_files(folder: Path) -> None:
    """Recursively unzip all compressed files in a folder and its subfolders.

    Args:
        folder: Path to the root folder to process
    """
    for file_path in tqdm(list(folder.rglob('*')), desc="Unzipping files"):
        if not is_file_compressed(file_path):
            continue

        extracted_path = file_path.with_suffix('')
        if extracted_path.exists():
            logger.info(f"Skipping {file_path.name} - already extracted")
            continue

        logger.info(f"Unzipping {file_path.name}...")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(file_path.parent)
        logger.info(f"Unzipped {file_path.name}")

        # Recursively handle nested archives
        unzip_files(extracted_path)


def parse_xml(xml_path: Path) -> Dict:
    """Parse a USPTO XML file to extract patent metadata and content.

    Args:
        xml_path: Path to the XML file

    Returns:
        Dictionary containing extracted patent information

    Raises:
        ValueError: If required XML elements are missing
    """
    def get_text_or_none(tag):
        return tag.get_text() if tag else None

    with open(xml_path, 'r', encoding='UTF-8') as f:
        soup = BeautifulSoup(f.read(), 'xml')

    # Extract core publication details
    title = soup.find('invention-title').get_text()
    pub_ref = soup.find('publication-reference')
    number = pub_ref.find('doc-number').get_text()
    date = pub_ref.find('date').get_text()

    # Get application ID with fallback
    try:
        application_id = soup.find('parent-doc').find('doc-number').get_text()
    except AttributeError:
        app_ref = soup.find('application-reference')
        application_id = app_ref.find('doc-number').get_text()

    # Get application type if available
    app_ref = soup.find('application-reference')
    application_type = app_ref['appl-type'] if app_ref else None

    # Extract classifications
    ipc_classifications = [
        ipc.get_text() for ipc in soup.find_all('classification-ipc')
    ]
    national_classifications = [
        nc.get_text() for nc in soup.find_all('classification-national')
    ]

    # Extract inventor information
    inventors = [
        {
            'last_name': inv.find('last-name').get_text(),
            'first_name': inv.find('first-name').get_text()
        }
        for inv in soup.find_all('applicant')
    ]

    # Extract main text content
    abstract = soup.find('abstract').get_text()
    description = soup.find('description').get_text()
    claims = "\n".join(
        claim.get_text(separator="\n", strip=True)
        for claim in soup.find_all('claim')
    )

    return {
        'title': title,
        'application_id': application_id,
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


def get_relevant_xml_files(folder: Path) -> List[Path]:
    """Find all relevant XML files in a folder, excluding sequence listings.

    Args:
        folder: Path to search for XML files

    Returns:
        List of paths to relevant XML files
    """
    return [
        path for path in folder.rglob('*.xml')
        if 'seqlst' not in path.name.lower()
    ]


def create_dataframe(folder_year: Path) -> Tuple[pd.DataFrame, List[Path]]:
    """Create a DataFrame from USPTO patent XML files in a folder.

    Args:
        folder_year: Path containing the XML files to process

    Returns:
        Tuple of (DataFrame containing patent data, List of failed files)
    """
    columns = [
        'title', 'publication_number', 'publication_date', 'application_type',
        'ipc_classifications', 'national_classifications', 'inventors',
        'abstract', 'description', 'claims'
    ]
    df = pd.DataFrame(columns=columns)
    error_files = []

    xml_files = get_relevant_xml_files(folder_year)

    for xml_path in tqdm(xml_files, desc="Parsing XML files"):
        try:
            parsed_data = parse_xml(xml_path)
            df = pd.concat(
                [df, pd.DataFrame([parsed_data])],
                ignore_index=True
            )
        except Exception as e:
            logger.error(f"Failed to parse {xml_path}: {str(e)}")
            error_files.append(xml_path)
            logger.info(f"Current DataFrame shape: {df.shape}")

    return df, error_files


def main() -> None:
    """Main execution function."""

    base_path = Path(
        r"C:\Users\Roberto\Documents\GitHub_repositories\USPTO\data"
    )

    folder_year = base_path / "images_and_text_data" / "2005"

    # Process files
    # unzip_files(folder_year)
    df, error_files = create_dataframe(folder_year)

    # Save error log
    error_log = folder_year / "error_files.txt"
    with open(error_log, "w") as f:
        f.write("\n".join(str(path) for path in error_files))

    # Calculate text statistics
    for col in TEXT_COLUMNS:
        df[f"{col}_characters"] = df[col].str.len()
        df[f"{col}_tokens"] = df[col].apply(count_tokens)

    # Save results
    output_file = folder_year / "dataframe.parquet"
    df.to_parquet(output_file, index=False)

    logger.info("DataFrame creation completed")
    logger.info(f"Number of failed files: {len(error_files)}")


if __name__ == "__main__":
    main()
