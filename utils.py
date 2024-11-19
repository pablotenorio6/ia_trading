import pandas as pd

def slprofit_strategy(df, profit, stop_loss, range) -> [str, int]:
    current_value = df['close'].iloc[0]  # El precio actual
    future_values = df['close'].iloc[1:range] if len(df['close'].iloc[1:]) >= range else df['close'].iloc[1:]
    i = range if len(df['close'].iloc[1:]) >= range else len(df['close'].iloc[:])
    # range precios siguientes
    # Buscar el primer valor que cumple las condiciones de +profit% o -stop-loss%
    for i, value in enumerate(future_values):
        percentage_change = (value - current_value) / current_value

        if percentage_change >= profit:
            if (pd.to_datetime(df.iloc[i+1]['timestamp']) - pd.to_datetime(df.iloc[i]['timestamp'])).total_seconds()/60 > 5:
                break
                # return ['Gap-Buy', i]
            else:
                return ['Buy', i]

        if percentage_change <= stop_loss:
            break
            # if (pd.to_datetime(df.iloc[i+1]['timestamp']) - pd.to_datetime(df.iloc[i]['timestamp'])).total_seconds()/60 > 5:
            #     return ['Gap-Sell', i]
            # else:
            #     return['Sell', i]

    return ['Sell', i]


def simple_strategy(df) -> [str, int]:
    current_value = df['close'].iloc[0]
    future_values = df['close'].iloc[1:10]
    if future_values.max() > current_value + current_value*0.003:
        return 'Buy'
    else:
        return 'Sell'


def transform_rsi_optimized(rsi_series):
    rsi_transformed = pd.Series(index=rsi_series.index, dtype=int)

    # Condiciones
    rsi_transformed[rsi_series > 70] = -1  # RSI > 70 -> -1
    rsi_transformed[rsi_series < 30] = 1  # RSI < 30 -> +1

    # Entre 30 y 70
    between_30_70 = (rsi_series >= 30) & (rsi_series <= 70)
    rsi_transformed[between_30_70] = (rsi_series.diff()[between_30_70] > 0).apply(lambda x: 1 if x else -1)

    return rsi_transformed


def discretize_features(df: pd.DataFrame) -> pd.DataFrame:
    df['MACD'] = df['MACD'].diff().apply(lambda x: 1 if x > 0 else -1)
    df['SMA'] = (df['close'] > df['SMA']).apply(lambda x: 1 if x else -1)
    df['EMA'] = (df['close'] > df['EMA']).apply(lambda x: 1 if x else -1)
    df['MOM'] = df['MOM'].apply(lambda x: 1 if x > 0 else -1)
    df['RSI'] = transform_rsi_optimized(df['RSI'])
    return df