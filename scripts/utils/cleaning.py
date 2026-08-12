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

if __name__ == "__main__":
    df = (pd.read_csv(
        "data/raw/Actual_generation_202607010000_202608010000_Quarterhour.csv",
        sep=';')
        )

    clean_df = clean_smard_generation(df)
    print(clean_df.info())