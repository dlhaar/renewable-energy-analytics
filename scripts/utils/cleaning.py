import pandas as pd

def clean_smard_generation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and reshape a raw SMARD generation export into long format.
    
    Input: wide-format DataFrame as downloaded from SMARD
           (Start date, End date, one column per energy source)
    Output: long-format DataFrame with columns:
            Start date, End date, energy_source, generation_mwh
    """
    df = df.copy()

    # 1. Fix comma-separated thousands in numeric columns

    excl_cols = ['Start date', 'End date', 'Nuclear [MWh] Original resolutions']
    selec_cols = [col for col in df.columns if col not in excl_cols]
    for c in selec_cols:
        df[c] = (df[c]
                 .astype(str)
                 .str
                 .replace(',','',regex=False)
                 .astype(float)
            )
        
    # 2. Handle the Nuclear placeholder/zero column

    df['Nuclear [MWh] Original resolutions'] = (
        df['Nuclear [MWh] Original resolutions']
        .replace('-',0,regex=False)
        .astype(float)
    )
    
    # 3. Convert Start date / End date to datetime
    df['Start date'] = pd.to_datetime(df['Start date'], format='%b %d, %Y %I:%M %p')
    df['End date'] = pd.to_datetime(df['End date'], format='%b %d, %Y %I:%M %p')
    
    # 4. Melt to long format
    df_long = df.melt(
        id_vars=['Start date', 'End date'],
        var_name='energy_source',
        value_name='generation_mwh'
    )
    
    # 5. Clean up energy_source column names
    df_long['energy_source'] = (
        df_long['energy_source']
        .str
        .replace(' [MWh] Original resolutions', '', regex=False)
    )

    return df_long



def clean_smard_price(df: pd.DataFrame) -> pd.DataFrame:
    """ 
    Clean SMARD day ahead prices 
    Input: Wide format dataframe downloaded from SMARD: start date,
    end date, one column per country
    Output: Long format with start and end date, country, and price eur/mwh
    
    
    """

    df = df.copy()

    # 1. Select the four columns that are needed
    df = df[['Start date',
             'End date',
             'Germany/Luxembourg [€/MWh] Original resolutions',
             'France [€/MWh] Original resolutions']]

    # 2. Convert Start date / End date to datetime
    df['Start date'] = pd.to_datetime(df['Start date'], format='%b %d, %Y %I:%M %p')
    df['End date'] = pd.to_datetime(df['End date'], format='%b %d, %Y %I:%M %p')

    # 3. Melt to long format
    df_long = df.melt(
        id_vars=['Start date', 'End date'],
        var_name='country',
        value_name='price_eur_mwh'
    )

    # 4. Clean country names

    df_long['country'] = (df_long['country']
        .str
        .replace(' [€/MWh] Original resolutions', '', regex=False)
    )

    return df_long

if __name__ == "__main__":

    #gen_data = 'data/raw/Actual_generation_202607010000_202608010000_Quarterhour.csv'
    price_data = 'data/raw/Day-ahead_prices_202607010000_202608010000_Quarterhour.csv'

    df = (pd.read_csv(
        price_data,
        sep=';')
        )

    clean_df = clean_smard_price(df)
    print(clean_df.info())

    print(clean_df.head())

    print(clean_df['country'].unique().tolist())