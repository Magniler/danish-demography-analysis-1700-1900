import os
from pathlib import Path
from typing import Any, Dict, Tuple
import pandas as pd
from pandas import DataFrame
import csv
import math

def clean_data_age_gender(census_df: DataFrame) -> tuple[DataFrame, float, int]:
    """Clean data for population pyramid analysis. Focuses on the age_in_full_years an 'køn' coloumns
    
    returns a tuple of:
        age_pyramid_df: cleaned data frame
        loss: Percentage of data lost during cleaning
        size_before: size of the data before cleaning
    """

    size_before = len(census_df)
    age_pyramid_df = census_df.copy(deep=True)
    
    # get the age_in_full_years coloumn to be the correct type
    age_pyramid_df_no_na = age_pyramid_df.dropna(subset=['age_full_years'])
    age_pyramid_df_no_na['age_in_full_years'] = age_pyramid_df_no_na['age_full_years'].astype(str).str.replace(' ', '')
    age_pyramid_df_no_na['age_in_full_years'] = age_pyramid_df_no_na['age_full_years'].astype(str).str.replace('', '')
    age_pyramid_df_no_na['age_in_full_years'].astype(str).str.strip().ne('')
    age_pyramid_df_no_na['age_full_years'] = age_pyramid_df_no_na['age_full_years'].round().astype(int)

    # standardize the sex column
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('(', '')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace(')', '')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('U', 'Unknown')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('??', 'Unknown')

    size_after = len(age_pyramid_df_no_na)

    return age_pyramid_df_no_na, (size_before - size_after) / size_before if size_before != 0 else 0, size_before


def split_csv(input_file, output_file1, output_file2):
    """
    Split a CSV file into two approximately equal parts.

    This function reads an input CSV file and divides its contents into two separate
    output CSV files. If the input file has an odd number of rows (including the header),
    the first output file will contain one more row than the second.

    Parameters:
    input_file (str): The path to the input CSV file to be split.
    output_file1 (str): The path where the first half of the split data will be saved.
    output_file2 (str): The path where the second half of the split data will be saved.

    Returns:
    None

    Raises:
    FileNotFoundError: If the input_file does not exist.
    PermissionError: If the script doesn't have permission to read the input file or write the output files.
    csv.Error: If there are issues reading or writing CSV data.

    Note:
    This function reads the entire input file into memory, so it may not be suitable for very large CSV files.
    For large files, consider using a streaming approach to reduce memory usage.
    """
    # Read the input CSV file
    with open(input_file, 'r', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    
    # Calculate the middle index
    middle = math.ceil(len(data) / 2)
    
    # Write the first half to output_file1
    with open(output_file1, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data[:middle])
    
    # Write the second half to output_file2
    with open(output_file2, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data[middle:])


def calculate_household_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate the average family size and standard deviation of family sizes in a DataFrame.
    Args:
        df (pd.DataFrame): a DataFrame containing a 'household_id' column
    Returns:
        Dict[str, Any]: the results of the calculation, including the average family size, standard deviation, total families, and all household sizes
    """
    # Count the number of individuals in each household
    household_sizes: pd.Series = df['household_id'].value_counts()
    
    # Calculate the average family size and standard deviation
    average_family_size: float = household_sizes.mean()
    std_family_size: float = household_sizes.std()
    
    # Get the total number of families
    total_families: int = household_sizes.size
    
    # Create a dictionary with the results
    results: Dict[str, Any] = {
        'average_family_size': average_family_size,
        'std_family_size': std_family_size,
        'total_families': total_families,
        'household_sizes': household_sizes.values  # Add this line to include all household sizes
    }
    
    return results

def make_master_csv_file(path_to_census_dir: Path):
    """Goes through the census directory and creates a master CSV file containing all data."""
    # Create an empty DataFrame to store the combined data
    combined_data = pd.DataFrame()
    list_if_dfs = []
    
    # Iterate over all CSV files in the directory
    for amt_dir in path_to_census_dir.iterdir():
        if amt_dir.is_dir():
            for file_path in amt_dir.glob('Rigsarkivet_folketælling*.csv'):
                df = pd.read_csv(file_path, delimiter='$')
                year = int(file_path.stem.split('_')[-1])
                amt = file_path.stem.split('_')[2]

                # Add year and amt columns
                df['year'] = year
                df['amt'] = amt
                
                # Append the DataFrame to the list
                list_if_dfs.append(df)
    
    # Write the combined data to a new CSV file
    combined_data = pd.concat(list_if_dfs)
    combined_file_path = Path(path_to_census_dir / 'combined_data_raw.csv')
    combined_data.to_csv(combined_file_path, index=False)
    
    return combined_file_path

if __name__ == "__main__":
    # Example usage of the functions
    make_master_csv_file(Path.cwd() / 'data' / 'census')