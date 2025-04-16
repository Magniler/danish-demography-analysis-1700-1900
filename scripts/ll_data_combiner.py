"""Script to combine data from all censuses into one file"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

cwd = Path.cwd()

if __name__ == "__main__":
    # Load data
    data_dir = cwd / "scripts" / "ll_data"
    files = os.listdir(data_dir)
    files = [f for f in files]
    data = [pd.read_csv(data_dir / f) for f in files]

    # Combine data
    combined_data = pd.concat(data)

    # Save data
    combined_data.to_csv(data_dir / "combined_ll_census_1787-1901", index=False)
