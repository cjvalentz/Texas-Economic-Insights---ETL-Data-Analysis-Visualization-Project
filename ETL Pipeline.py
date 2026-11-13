import pandas as pd
import requests
from sqlalchemy import create_engine

api_key = "9faba82510fbf04cdaef058a750f6f18c9d53495"

pop_url = ("https://api.census.gov/data/2024/acs/acs5?get=NAME,B01003_001E&for=county:*&in=state:48&")

income_url = ("https://api.census.gov/data/2024/acs/acs5?get=NAME,B19013_001E&for=county:*&in=state:48&")

#Extract population data from the API

pop_response = requests.get(pop_url, params={"key": api_key})

pop_response.raise_for_status()

population_data = pop_response.json()

#Conversion of the population data to a pandas DataFrame
population_df = pd.DataFrame(
    population_data[1:], 
    columns=population_data[0]
    )

#Extract income data
income_response = requests.get(income_url, params={"key": api_key})

income_response.raise_for_status()

income_data = income_response.json()

#Conversion of the income data to a pandas DataFrame
income_df = pd.DataFrame(
    income_data[1:], 
    columns=income_data[0]
    )

#Renaming the columns to be more clear
population_df = population_df.rename(columns={
    "NAME": "County",
    "B01003_001E": "Population"
})

income_df = income_df.rename(columns={
    "NAME": "County",
    "B19013_001E": "Median_Income"
})

#Join the columns
combined_df = pd.merge(
    population_df, 
    income_df, 
    on=["County", "state", "county"],
    how="inner"
)

#Renaming the state and second county columns to state_fips and county_fips for clarity
combined_df = combined_df.rename(columns={
    "state": "state_fips",
    "county": "county_fips"
})

#Getting information about the combined DataFrame:
print(combined_df.head())

#Converting the Population and Median_Income columns to numeric types
combined_df["Population"] = pd.to_numeric(combined_df["Population"], errors='coerce')
combined_df["Median_Income"] = pd.to_numeric(combined_df["Median_Income"], errors='coerce')

print(combined_df.info())

print(combined_df.describe())

print(combined_df.isnull().sum())

#Optional: Download the combined DataFrame to a CSV file 
combined_df.to_csv("combined_census_data.csv", index=False)

## Load the data into a SQL database

engine = create_engine('sqlite:///census_data.db')

combined_df.to_sql(
    'census_data', 
    con=engine, 
    if_exists='replace', 
    index=False
    )
