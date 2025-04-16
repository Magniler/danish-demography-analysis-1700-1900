"""scripts to generate population pyramids"""
from pathlib import Path
import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
import plotly.graph_objs as go

import helper_functions as hf

#Future proofing of the way we use pandas
pd.options.mode.copy_on_write = True

def check_date(date: str, year: int) -> int:
    """Uses a date and a year to find the age of a person, if the date isn't a properly formatted date it will return the input value"""
    if date == '':
        return date
    try:
        date_split = date.split('.')
    except Exception as _:
        return date
    if len(date_split) != 3:
        return date
    return year - int(date_split[2])

def clean_data_age_gender(census_df: DataFrame, year) -> tuple[DataFrame, float, int]:
    """Clean data for population pyramid analysis. Focuses on the age_in_full_years an 'køn' coloumns
    
    returns:
        age_pyramid_df: cleaned data frame
        loss: Percentage of data lost during cleaning 
    """

    size_before = len(census_df)
    age_pyramid_df = census_df.copy(deep=True)
    # get the age_in_full_years coloumn to be the correct type
    age_pyramid_df_no_na = age_pyramid_df.dropna(subset=['age_full_years'])
    age_pyramid_df_no_na['age_in_full_years'] = age_pyramid_df_no_na['age_full_years'].astype(str).str.replace(' ', '')
    age_pyramid_df_no_na['age_in_full_years'] = age_pyramid_df_no_na['age_full_years'].astype(str).str.replace('', '')
    age_pyramid_df_no_na['age_in_full_years'].astype(str).str.strip().ne('')
    age_pyramid_df_no_na['age_full_years'] = age_pyramid_df_no_na['age_full_years'].round().astype(int)
    #Clean up the age coloumn for analysis
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('[^0-9][^0-9]', '', regex=True)
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('[a-zA-Z]+', '', regex=True)
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('[!#&%?-]', '', regex=True)
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('(', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace(')', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace(']', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('[', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('½', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('1/2', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('1/4', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('3/4', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('3/12', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace(' ', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace(',', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('/', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('\'', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('+', '')
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('*', '') # TODO Might be interesting to look at the sources and see what these are
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].str.replace('(?<!\w)\.(?!\w)', '', regex=True) # Only remove standalone dots
    # age_pyramid_df['age_in_full_years'] = age_pyramid_df['age_in_full_years'].apply(lambda x: check_date(x, int(year)))
    # age_pyramid_df.drop(age_pyramid_df[age_pyramid_df['age_in_full_years'] == ''].index, inplace=True)

    # standardize the sex column
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('(', '')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace(')', '')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('U', 'Unknown')
    age_pyramid_df_no_na['køn'] = age_pyramid_df_no_na['køn'].str.replace('??', 'Unknown')

    size_after = len(age_pyramid_df_no_na)

    return age_pyramid_df_no_na, (size_before - size_after) / size_before if size_before != 0 else 0, size_before

def create_population_pyramid(age_pyramid_df: pd.DataFrame, year: str, area: str) -> go.Figure:
    """Creates a population pyramid from the given data frame

    Args:
        age_pyramid_df (pd.DataFrame): Dataframe with the given data, must contain the columns 'Alder' and 'køn' and be cleaned

    Returns:
        go.Figure: Plotly figure of the population pyramid
    """
    age_pyramid_df['Alders_groupe'] = pd.cut(
                            age_pyramid_df['age_full_years'], 
                            bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 2000],
                            labels=['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90+']
    )

    age_pyramid_df = age_pyramid_df.groupby(['Alders_groupe', 'køn']).size().unstack().reset_index()
    y = age_pyramid_df['Alders_groupe']
    x_m = age_pyramid_df['M']
    x_f = age_pyramid_df['K'] * -1 # negative to make it go the other way

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=y,
            x=x_m,
            name='Male',
            orientation='h',
    ))

    fig.add_trace(
        go.Bar(
            y=y,
            x=x_f,
            name='Female',
            orientation='h',
    ))

    fig.update_layout(
        template = 'plotly_white',
        title = f'Age Pyramid of {area} for {year}',
        title_font_size = 24,
        barmode='relative',
        bargap=0.0,
        bargroupgap=0.0,
    )

    return fig


def main():
    """Main loop for going through the cleaning and plotting of the population pyramid"""


    # Get in the data
    base_path = Path.cwd()
    census_data_dir = base_path / 'data' / 'census'
    image_data_dir = base_path / 'data' / 'images'
    image_data_dir.mkdir(exist_ok=True)
    removal_list = {}

    for dir in census_data_dir.iterdir():
        if dir.is_dir():
            for file in dir.iterdir():
                if file.suffix != '.csv':
                    continue
                data: DataFrame = pd.read_csv(filepath_or_buffer=file, delimiter='$')
                year = file.stem.split('_')[-1]
                data, removal, total_for_that_year = clean_data_age_gender(data, year)
                removal_list[year] = (removal, total_for_that_year)

                #  Create population pyramid
                fig: go.Figure = create_population_pyramid(data, year, dir.stem)


                # Save the plot

                path_to_save_plot = image_data_dir / dir.stem / f'population_pyramid_{file.stem}.svg'
                path_to_save_plot.parent.mkdir(exist_ok=True)
                fig.write_image(path_to_save_plot)
    
            # Make a quick plot of the data loss 
            fig, ax = plt.subplots()
            fig: plt.Figure = fig
            x = list(removal_list.keys())
            y = [removal_list[year][0] for year in x]
            total = [removal_list[year][1] for year in x]
            ax.bar(x, y)
            ax.set_ylabel('Percentage of data removed')
            ax.set_xlabel('Year')
            ax.set_title('Data removed during cleaning')
            ax2 = ax.twinx()
            ax2.plot(x, total, color='red')
            ax2.set_ylabel('Total number of entries')
            fig.savefig(image_data_dir / f'data_cleaning{dir.stem}.png')

if __name__ == '__main__':
    main()