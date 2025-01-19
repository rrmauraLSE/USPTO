"""Module for determining gender from first names."""

import gender_guesser.detector as gender
from pathlib import Path


# Constants
SSA_FOLDER = Path(
    r"C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\names_US_SSA"
)
LIST_NAME_UNKNOWNS = []


def create_name_gender_count_dict():
    """
    Create a dictionary mapping names to counts of males/females from SSA data.

    Returns:
        dict: Mapping of names to counts by gender 
            {'name': {'male': count, 'female': count}}
    """
    names2sex_count = {}

    for file in SSA_FOLDER.glob('*'):
        with open(file, 'r') as f:
            for line in f:
                name, gender, count = line.strip().split(',')
                name = name.lower()

                if name not in names2sex_count:
                    names2sex_count[name] = {'male': 0, 'female': 0}
                if gender == 'M':
                    names2sex_count[name]['male'] += int(count)
                elif gender == 'F':
                    names2sex_count[name]['female'] += int(count)

    return names2sex_count


def clean_name(name: str) -> str:
    """
    Clean a name by removing spaces and hyphens and taking first component.

    Args:
        name: The name to clean

    Returns:
        str: The cleaned name
    """
    # Take first part if name contains space or hyphen
    if ' ' in name:
        name = name.split(' ')[0]
    if '-' in name:
        name = name.split('-')[0]

    return name.lower()


def get_gender(first_name: str) -> str:
    """
    Determine gender associated with a given first name.

    Uses SSA data first, falls back to gender-guesser library.

    Args:
        first_name: The first name to check

    Returns:
        str: Predicted gender 
    """
    first_name = clean_name(first_name)

    # Check SSA data first
    if first_name in dict_names:
        count_dict = dict_names[first_name]
        if count_dict['male'] > count_dict['female']:
            return 'male'
        return 'female'

    # Fall back to gender-guesser
    gender_prediction = d.get_gender(first_name)
    if gender_prediction != 'unknown':
        return gender_prediction

    LIST_NAME_UNKNOWNS.append(first_name)
    return 'unknown'


def get_list_genders(inventors):
    """
    Get gender predictions for a list of inventors.

    Args:
        inventors: List of inventor dictionaries containing 'first_name' key

    Returns:
        list: List of predicted genders
    """
    return [get_gender(inventor['first_name']) for inventor in inventors]


if __name__ == '__main__':
    # Initialize detector
    d = gender.Detector(case_sensitive=False)

    # Create name-gender mapping from SSA data
    dict_names = create_name_gender_count_dict()

    # Test examples
    print(d.get_gender('Francois'))  # male
    print(d.get_gender('Pauley'))    # andy
    print(dict_names['emily'])       # SSA data for Emily
