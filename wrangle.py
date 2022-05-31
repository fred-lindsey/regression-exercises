# Functions in this WRANGLE file:

# get_connection('db') : retrieves databases for use, by name

# get_zillow_data(): acquires Zillow Data from the CodeUp db

# prep_zillow(df): removes nulls, drops duplicates, formats float to int,
# removes 0 value columns for BD/BR/SQ FT

# wrangle_zillow(): combination of the two above functions that produces a 
# complete, clean data set

#_____________________________________________________________________________

# Required imports for these files:

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import env
import os

#_____________________________________________________________________________

def get_connection(db, user=env.user, host=env.host, password=env.password):
    return f'mysql+pymysql://{user}:{password}@{host}/{db}'

#____________________________________________________________________________________

def get_zillow_data(use_cache=True):
    """Retrieves zillow data set either from a local CSV (if it exists),
    or from a SQL query to the CodeUp DB.
    Parameters: BEDROOMCNT, BATHROOMCNT, CALCULATEDFINISHEDSQUAREFEET, 
    TAXVALUEDOLLARCNT, YEARBUILT, TAXAMOUNT, FIPS for all Single Family
    Residential properties in 2017 data set (inferred and labeled)"""
    filename = "zillow.csv"
    if os.path.isfile(filename) and use_cache:
        return pd.read_csv(filename)
    else:
        df = pd.read_sql("""
        SELECT parcelid, bedroomcnt, bathroomcnt, calculatedfinishedsquarefeet,
        taxvaluedollarcnt, yearbuilt, taxamount, fips
        FROM properties_2017
        JOIN propertylandusetype USING (propertylandusetypeid)
        WHERE (propertylandusetypeid = 261) 
        OR (propertylandusetypeid = 279);
        """
        , get_connection('zillow'))
        df.to_csv(filename, index=False)
        return df

#__________________________________________________________________________________

def prep_zillow(df):
    """
    Takes in zillow Dataframe from the get_zillow_data function.
    Arguments: drops unnecessary columns, 0 value columns, duplicates,
    and converts select columns from float to int.
    Returns cleaned data.
    """
    # remove empty entries stored as whitespace, convert to nulls
    df = df.replace(r'^\s*$', np.nan, regex=True)
    # drop null rows
    df = df.dropna()
    # drop any duplicate rows
    df = df.drop_duplicates(keep='first')
    # convert column types from float to int
    df = df.astype({'bedroomcnt': int, 'fips': int,
          'calculatedfinishedsquarefeet': int, 'yearbuilt': int})
    # remove homes with 0 BR/BD or SQ FT from the final df
    df = df[(df.bedroomcnt != 0) & (df.bathroomcnt != 0) & 
    (df.calculatedfinishedsquarefeet >= 69)]

    return df

#__________________________________________________________________________________

def wrangle_zillow():
    df = get_zillow_data()
    df = prep_zillow(df)
    return df
