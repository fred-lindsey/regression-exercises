# Functions in this WRANGLE file:

# get_connection('db') : retrieves databases for use, by name

# get_zillow_data(): acquires Zillow Data from the CodeUp db

# prep_zillow(df): removes nulls, drops duplicates, formats float to int,
# removes 0 value columns for BD/BR/SQ FT

# wrangle_zillow(): combination of the two above functions that produces a 
# complete, clean data set

# fit_and_scale(scaler, train, validate, test): takes in 

#____________________________________________________________________________________

# Required imports for these files:

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import env
import os
import sklearn.preprocessing
from sklearn.model_selection import train_test_split
#____________________________________________________________________________________

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
# outlier handling to remove quant_cols with >3.5 z-score (std dev)
def remove_outliers(threshold, quant_cols, df):
    z = np.abs((stats.zscore(df[quant_cols])))
    df_without_outliers=  df[(z < threshold).all(axis=1)]
    print(df.shape)
    print(df_without_outliers.shape)
    return df_without_outliers
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
    df = df.astype({'fips': int, 'parcelid': object})
    # remove homes with 0 BR/BD or SQ FT from the final df
    df = df[(df.bedroomcnt != 0) & (df.bathroomcnt != 0) & 
    (df.calculatedfinishedsquarefeet >= 69)]
    # remove all rows where any column has z score gtr than 3
    non_quants = ['fips', 'parcelid']
    quants = df.drop(columns=non_quants).columns
    # outlier handling
    # remove numeric values with > 3.5 std dev
    df = remove_outliers(3.5, quants, df)

    return df
#__________________________________________________________________________________

def wrangle_zillow():
    df = get_zillow_data()
    df = prep_zillow(df)
    return df

#__________________________________________________________________________________

#scaler = sklearn.preprocessing.MinMaxScaler()
#scaler = sklearn.preprocessing.StandardScaler()
#scaler = sklearn.preprocessing.RobustScaler()
#pick the scaler and specify in the parameters


def fit_and_scale(scaler, train, validate, test):
    # only scales float columns
    floats = train.select_dtypes(include='float64').columns
    # fits scaler to training data only, then transforms
    # train, validate & test
    scaler.fit(train[floats])
    scaled_train = pd.DataFrame(data=scaler.transform(train[floats]), columns=floats)
    scaled_validate = pd.DataFrame(data=scaler.transform(validate[floats]), columns=floats)
    scaled_test = pd.DataFrame(data=scaler.transform(test[floats]), columns=floats)
    return scaled_train, scaled_validate, scaled_test
