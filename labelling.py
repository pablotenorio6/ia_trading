import pandas as pd
import talib as ta
import logging
import numpy as np
from utils import slprofit_strategy, discretize_features, simple_strategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def get_volatility(df: pd.DataFrame) -> pd.DataFrame:
    # Estudiar la volatilidad diaria en horario de mercado
    df = df[['timestamp', 'close']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[(df['timestamp'].dt.hour >= 10) & (df['timestamp'].dt.hour < 16)]
    # Agrupar por día
    df.set_index('timestamp', inplace=True)
    df['date'] = df.index.date
    max_values = df.groupby('date')['close'].max()
    min_values = df.groupby('date')['close'].min()
    avg = df.groupby('date')['close'].mean()
    volatility = (max_values - min_values)/avg
    return volatility


# Add indicators to raw_data
def labelling_data(df: pd.DataFrame(), idx: int) -> pd.DataFrame():
    df['RSI'] = ta.RSI(df['close'], timeperiod=7)
    df['MACD'], df['Signal'], df['Hist'] = ta.MACD(df['close'], fastperiod=5, slowperiod=13, signalperiod=9)
    df['EMA'] = ta.EMA(df['close'], timeperiod=10)
    df['SMA'] = ta.SMA(df['close'], timeperiod=10)
    df['MOM'] = ta.MOM(df['close'], timeperiod=10)
    # df['AD'] = ta.OBV(df['close'], df['volume'])
    # __, df['middleBollinger'], __ = ta.BBANDS(df['close'], timeperiod=20)


    # Add result based on stop-loss/take-profit, for reference lets start with 0.5% take profit and 0.2% stop loss and evaluation periods of 240 interval
    # results = [slprofit_strategy(df.iloc[i:i+136], profit=0.005, stop_loss=-0.002, range=136) for i in range(len(df))]
    # df['selling-time'] = [x[1] for x in results]
    # df['buy-sl'] = [x[0] for x in results]
    # Lets start with an easy one, positive if avg next 5 values is above prize
    # df['buy-sl'] = [simple_strategy(df.iloc[i:i+10]) for i in range(len(df))]


    df = df.dropna()
    volatility = get_volatility(df)
    df.drop(columns=['Unnamed: 0', 'Signal', 'Hist'], inplace=True)
    logging.info('Indicators aggregated')
    df.to_csv(f'labelled_data/202{idx}_labelled_data.csv')
    return df



if __name__ == '__main__':
    for i in range(1, 5):
        labelling_data(pd.read_csv(f'raw_data/202{i}_data.csv'), i)