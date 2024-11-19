### Trials with polygon API and Coca-Cola

import requests
import pandas as pd
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

API_KEY = os.getenv("API_KEY")
symbol = "KO"

# Define las fechas de inicio y fin
interval = "5"  # Velas de 5 minutos

def polygon_trial():
    for i in range(3, 24):

        # Construir la solicitud
        start_date = f"200{i}-01-01" if i < 10 else f"20{i}-01-01"
        end_date = f"200{i}-12-31" if i < 10 else  f"20{i}-12-31"
        url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{interval}/minute/{start_date}/{end_date}?adjusted=true&sort=asc&limit=50000&apiKey={API_KEY}"

        # Realiza la solicitud
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                # Convierte a DataFrame
                df = pd.DataFrame(data['results'])
                # Formatea el timestamp
                df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                clean_data = df[['vw', 'timestamp']]
                clean_data.to_csv()
            else:
                print("No se encontraron resultados.")
        else:
            print(f"Error: {response.status_code}, {response.text}")



def alphavantage_trial():
    ALPHA_KEY = "CLMCZZL2MAND1HPW"

    for i in range(21, 23):
        annual_df = pd.DataFrame()
        year = f"20{i}" if i > 9 else f"200{i}"
        for k in range(1, 13):
            try:
                month = f"{k}" if k > 9 else f"0{k}"
                # URL del endpoint de Alpha Vantage
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_KEY}&month={year}-{month}&outputsize=full&extended_hours=true"

                # Realizamos la solicitud HTTP
                response = requests.get(url)
                data = response.json()

                # Convertimos los datos a un DataFrame
                if "Time Series (5min)" in data:
                    df = pd.DataFrame(data["Time Series (5min)"]).T
                    df = df.astype(float)  # Aseguramos que los valores sean numéricos
                    df['timestamp'] = pd.to_datetime(df.index)
                    clean_df = df[['timestamp', '4. close', '5. volume']]
                    clean_df = clean_df.iloc[::-1].reset_index(drop=True)
                    annual_df = pd.concat([annual_df, clean_df])

                if k % 4 == 0:
                    time.sleep(70)

            except Exception as e:
                logging.exception(f'Could not do {year}-{month}')

        logging.info(f'Year {year} recovered')
        annual_df.to_csv(f"raw_data/{year}_data.csv")


if __name__ == "__main__":
    alphavantage_trial()