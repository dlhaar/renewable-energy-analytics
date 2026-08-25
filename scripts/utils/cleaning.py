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


def clean_entsoe_generation(df: pd.DataFrame, country: str) -> pd.DataFrame:
    """
    Clean and reshape a raw ENTSO-E generation pull (from entsoe-py) into
    long format, resampled to hourly to match the coarsest grain across
    countries.

    Input: DataFrame from client.query_generation(), MultiIndex columns
           (production_type, 'Actual Aggregated'/'Actual Consumption')
    Output: long-format DataFrame with columns:
            datetime, energy_source, generation_mw, country
    """
    df = df.copy()

    # 1. Keep only 'Actual Aggregated' (generation) columns — drop
    #    'Actual Consumption' (storage/consumption side, out of scope)
    df = df.loc[:, df.columns.get_level_values(1) == 'Actual Aggregated']

    # 2. Flatten the MultiIndex down to just the production type name
    df.columns = df.columns.get_level_values(0)

    # 3. Resample to hourly. Using .mean() rather than .sum() because
    #    ENTSO-E generation values represent MW (average power during
    #    the interval), not MWh (energy) like SMARD's export — averaging
    #    is the correct way to combine sub-hourly power readings into an
    #    hourly figure. NOTE: this means generation_mw here is NOT
    #    directly comparable to SMARD's generation_mwh without an
    #    explicit unit conversion later — flagging this now as a known
    #    issue to handle deliberately in Sprint 4, not silently.
    df = df.resample('h').mean()

    # 4. Move the datetime index into a real column
    df = df.reset_index().rename(columns={'index': 'datetime'})

    # 5. Melt to long format
    df_long = df.melt(id_vars='datetime', var_name='energy_source', value_name='generation_mw')

    # 6. Tag with country — since this function may be called once per
    #    country, the caller needs a way to distinguish rows after
    #    combining multiple countries' output later
    df_long['country'] = country

    # 7. Drop rows with no data (e.g. France's 'Energy storage' column,
    #    which came back entirely NaN — structurally absent, not a gap
    #    to fill). Dropping explicitly here, rather than leaving NaNs to
    #    surprise someone downstream, similar to how Nuclear was handled
    #    for SMARD — but this is a *different* kind of decision: Nuclear
    #    was real zeros, this is genuinely missing/inapplicable data.
    df_long = df_long.dropna(subset=['generation_mw'])

    return df_long

def load_entsoe_csv(filepath: str) -> pd.DataFrame:
    """
    Load a saved ENTSO-E generation CSV, reconstructing the MultiIndex
    columns and tz-aware DatetimeIndex that don't survive a plain
    to_csv()/read_csv() round-trip.
    """
    df = pd.read_csv(filepath, header=[0, 1], index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


if __name__ == "__main__":


    fr_data = 'data/raw/entsoe_fr_generation_2024-08-01_2026-08-01.csv'

    fr_load_data = load_entsoe_csv(fr_data)
    fr_clean = clean_entsoe_generation(fr_load_data, country='France')
    print(fr_clean.shape)
    print(fr_clean['energy_source'].unique())
    print(fr_clean.isna().sum())
    print(fr_clean.groupby('energy_source').size().sort_values())