import os
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
import pandas as pd


def fetch_entsoe_generation(country_code: str, start: pd.Timestamp, end: pd.Timestamp, save_path: str) -> pd.DataFrame:
    """
    Pull generation data from the ENTSO-E API for a given country and
    date range, save it to CSV, and return the raw DataFrame.
    """
    load_dotenv()
    client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))
    
    df = client.query_generation(country_code, start=start, end=end)
    df.to_csv(save_path)
    
    return df


if __name__ == "__main__":
    start = pd.Timestamp('2024-08-01', tz='Europe/Paris')
    end = pd.Timestamp('2026-08-01', tz='Europe/Paris')

    fr_generation = fetch_entsoe_generation(
        country_code='FR',
        start=start,
        end=end,
        save_path='data/raw/entsoe_fr_generation_2024-08-01_2026-08-01.csv'
    )