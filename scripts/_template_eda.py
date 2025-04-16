# imports
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import plotly.graph_objs as go
import json
from typing import List, Any, Dict

from helper_functions import clean_data_age_gender, split_csv, calculate_household_stats

#Future proofing of the way we use pandas
pd.options.mode.copy_on_write = True


# import test data
census_data_dir = Path.cwd().parent / 'data' / 'census'

# we load in the first of the census to explore that data
first_census_df = pd.read_csv(census_data_dir / "copenhagen" / 'Rigsarkivet_folketælling_Kobenhavn_amt_1787.csv', delimiter='$')

# We still clean the age and sex coloumns for now
cleaned_census_df, _, _ = clean_data_age_gender(first_census_df)

# Generator for csv files
csv_files = census_data_dir.glob('*/Rigsarkivet_folketælling*.csv')


# Generic Processing function to process the files

# Function to process each file and extract family size
def process_file(file_path: Path) -> pd.DataFrame:
    if isinstance(file_path, str):
        file_path = Path(file_path)
    df = pd.read_csv(file_path, delimiter='$')
    year = int(str(file_path.stem).split('_')[-1].split('.')[0])  # Extract year from filename
    amt = str(object=file_path.stem).split('_')[2]  # Extract amt from filename

    # Below here we can add the processing of the data