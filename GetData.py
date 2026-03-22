'''
GetData.py

In this script, the function to obtain the classification data and match results of the LaLiga is defined, using Selenium to navigate the website and BeautifulSoup to parse the HTML content. Then, a range of seasons and matchdays is iterated to obtain the corresponding data and save it into Excel files separated by season, with each matchday in a different sheet.
Parameters for the range of seasons and matchdays to process are also defined. Thus, the main program is responsible for executing the complete data extraction and storage process.

Author: Miguel Ángel Martín

Date: 22/03/2026
'''



# == Import libraries ==
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from io import StringIO
import os


# == Working directory ==
wd = os.path.dirname(os.path.abspath(__file__))



# == Parameters ==
start_year_first_season = 1997
start_year_last_season = 1997
matchday_start = 1
matchday_end = 2


# == Function to get classification data ==
def get_classification(driver, season, matchday):
    '''
    Function to obtain the classification data of the LaLiga for a given season and matchday.
    
    Parameters:
    driver (webdriver): Selenium driver used to navigate the webpage.
    season (str): Season in format "YYYY-YY" (e.g., "2023-24").
    matchday (int): Matchday number (e.g., 1, 2, ..., 38).     
    
    Returns:
    pd.DataFrame: DataFrame containing the classification for the specified season and matchday.
    '''

    # == Get data ==
    url = "https://www.bdfutbol.com/en/t/t" + season + ".html" 

    driver.get(url)

    # Wait until the select is present
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "jornada"))
    )

    select = Select(select_element)
    select.select_by_value(str(matchday)) 

    # Wait until the classification table is visible
    table_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "classific"))
    )

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Table containing the relevant data
    table = soup.find("table", {"id": "classific"})

    df = pd.read_html(StringIO(str(table)))[0]

    # Columns to remove
    cols_to_remove = ["Unnamed: 0", "Unnamed: 2"]

    # Drop columns and rename others
    df = df.drop(columns=[col for col in cols_to_remove if col in df.columns])
    df = df.rename(columns={"Unnamed: 1": "Position", "Unnamed: 3": "Team", "Pts.": "Pts"})

    return df


# == Function to get match results ==
def get_matches(driver, season, matchday):
    '''
    Function to obtain match results of the LaLiga for a given season and matchday.

    Parameters:
    driver (webdriver): Selenium driver used to navigate the webpage.
    season (str): Season in format "YYYY-YY" (e.g., "2023-24").
    matchday (int): Matchday number (e.g., 1, 2, ..., 38).
    
    Returns:
    pd.DataFrame: DataFrame containing match results for the specified season and matchday.   
    '''

    # == Get data ==
    url = "https://www.bdfutbol.com/es/t/t" + season + ".html?tab=results&jornada=" + str(matchday)

    driver.get(url)

    # Wait until the results table is visible
    table_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "resultats"))
    )

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Table containing the relevant data
    table = soup.find("table", {"class": "taula_estil taula_estil-16"})

    df = pd.read_html(StringIO(str(table)))[0]

    # Drop unnecessary columns and rename others
    df = df.drop(columns=["Fecha", "Estadio", "Unnamed: 2"])
    df = df.rename(columns={"Local": "Home", "Visitante": "Away", "Árbitro": "Referee"})

    return df


# == Main program ==

save_folder = wd + "/Data"

# Ensure subdirectories exist
os.makedirs(save_folder + "/Classification", exist_ok=True)
os.makedirs(save_folder + "/Matches", exist_ok=True)

driver = webdriver.Chrome()

# Iterate through seasons and matchdays, extract data and save into Excel files
for start_year in range(start_year_first_season, start_year_last_season + 1): 

    end_year_short = str(start_year + 1)[-2:]  # last 2 digits of next year
    season = f"{start_year}-{end_year_short}"

    file_name = f"Season {season}.xlsx"

    print("\Season:", season)

    # Use ExcelWriter to store each matchday in a different sheet
    writer1 = pd.ExcelWriter(save_folder + "/Classification/" + file_name, engine="xlsxwriter")
    writer2 = pd.ExcelWriter(save_folder + "/Matches/" + file_name, engine="xlsxwriter")
    
    for matchday in range(matchday_start, matchday_end + 1):

        print("\n     Matchday:", matchday, "\n")

        # Get data for current matchday
        df_classification = get_classification(driver, season, matchday)
        df_matches = get_matches(driver, season, matchday)

        # Save each matchday in a different sheet
        sheet_name = f"Matchday {matchday}"

        df_classification.to_excel(writer1, sheet_name=sheet_name, index=False)
        df_matches.to_excel(writer2, sheet_name=sheet_name, index=False)

    # Close writers to save files properly
    writer1.close()
    writer2.close()

    print("\n Data saved for Season:", season)

# Close Selenium driver
driver.quit()