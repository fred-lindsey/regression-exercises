
# Functions in this PREPARE file:

# prep_iris(): function notes below

# prep_titanic(): function notes below

# prep_telco(): function notes below

# encode_telco(): function notes below

#_____________________________________________________________________________

# Required imports for these files:

import pandas as pd

#_____________________________________________________________________________
def prep_iris(df):
    """
    Takes in the iris dataframe and returns a cleaned dataframe
    Arguments: df - a pandas dataframe with the expected feature name and columns
    Returns: clean_df - a dataframe with cleaning performed on it
    
    """
    #drop columns
    df = df.drop('species_id', 1)
    #renamed species name to species
    df = df.rename(columns={"species_name" : "species"})
    #encoded categorical variables
    dummy_df = pd.get_dummies(df[['species']], dummy_na=False, drop_first=[True, True])
    #concat the table
    df = pd.concat([df, dummy_df], axis=1)

    return df

# _____________________________________________________________________

def prep_titanic(df):
    """
    Takes in the titanic dataframe and returns a cleaned dataframe.
    Arguments: takes in the dataset and removes duplicates, encodes
    categorical data
    Returns: cleaned dataset
    
    
    """

    # drop uneeded columns
    df.drop_duplicates(inplace=True)
    cols_to_drop = ['embarked', 'class', 'passenger_id']
    df = df.drop(columns = cols_to_drop)
    # encode the categorical data
    dummy_df = pd.get_dummies(df[['embark_town', 'sex', 'deck']], 
                          dummy_na = False, drop_first=[True, True])
    #concat the two dataframes
    df = pd.concat([df, dummy_df], axis=1)
    
    return df


# _____________________________________________________________________

def prep_telco(df):
    """
    Takes in Telco_Churn Dataframe.
    Arguments: drops unnecessary columns   
    Returns cleaned data.
    """
    #drop unneeded columns
    df.drop(columns=['internet_service_type_id', 
                 'payment_type_id', 'contract_type_id'], inplace=True)
    #drop null values stored as whitespace:
    df['total_charges'] = df['total_charges'].str.strip()
    df = df[df.total_charges != ""]
    #convert to correct data type:
    df['total_charges'] = df.total_charges.astype(float)

    return df




def encode_telco(df):
    """
    Takes in Telco_Churn Dataframe.
    Encodes categorical data.    
    Returns encoded_df.
    """
    #Get dummies for non-binary categorical variables:
    dummies_list = df.select_dtypes('object').columns
    dummies_list = dummies_list.drop(['customer_id'])
    dummy_df = pd.get_dummies(df[dummies_list], dummy_na = False, drop_first=True)
    #concatenate the two dataframes
    df = pd.concat([df, dummy_df], axis=1)
    #rename the encoded df
    encoded_df = df.drop(columns=dummies_list)
    #return the encoded df
    return encoded_df


    #