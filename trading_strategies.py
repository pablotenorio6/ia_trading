"""
Estrategias de trading para análisis técnico
"""
import pandas as pd
import numpy as np


def aggregate_volume_15min(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega el volumen de datos de 5 minutos a intervalos de 15 minutos
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample a 15 minutos sumando el volumen y tomando el último precio de cierre
    df_15min = df.resample('15min').agg({
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    df_15min.reset_index(inplace=True)
    return df_15min


def detect_uptrend(prices: pd.Series, window: int = 3) -> bool:
    """
    Detecta tendencia alcista basada en los últimos precios
    """
    if len(prices) < window:
        return False
    
    recent_prices = prices.tail(window)
    # Tendencia alcista si los precios están generalmente subiendo
    return recent_prices.iloc[-1] > recent_prices.iloc[0] and recent_prices.is_monotonic_increasing


def calculate_volume_threshold(volume_series: pd.Series, multiplier: float = 1.5) -> float:
    """
    Calcula el umbral de volumen basado en la media histórica
    """
    volume_mean = volume_series.rolling(window=20, min_periods=10).mean()
    return volume_mean * multiplier


def _execute_volume_strategy(df: pd.DataFrame, buy_signals: pd.Series, 
                           trend_window: int = 3, exit_periods: int = 12,
                           stop_loss: float = -0.005, take_profit: float = 0.02) -> pd.DataFrame:
    """
    Función base común para ejecutar estrategias de volume breakout
    
    Args:
        df: DataFrame con datos de 5 minutos (ya procesado)
        buy_signals: Serie booleana con las señales de compra pre-calculadas
        trend_window: Ventana para detectar tendencia alcista
        exit_periods: Número de períodos para mantener la posición
        stop_loss: Porcentaje de pérdida para salir
        take_profit: Porcentaje de ganancia para salir
    
    Returns:
        DataFrame con señales de trading ejecutadas
    """
    result_df = df.copy()
    result_df['buy_signal'] = False
    result_df['sell_signal'] = False
    result_df['position'] = 0
    result_df['entry_price'] = 0.0
    result_df['exit_price'] = 0.0
    result_df['exit_reason'] = ''
    
    position = 0
    entry_timestamp = None
    entry_price = 0
    entry_index = None
    
    # Procesar señales
    for i, row in result_df.iterrows():
        current_time = row['timestamp']
        current_price = row['close']
        
        # Verificar señal de compra
        if buy_signals.loc[i] and position == 0:
            # Verificar horario válido para trades diarios
            if current_time.hour < 16 or (current_time.hour == 16 and current_time.minute < 55):
                result_df.loc[i, 'buy_signal'] = True
                result_df.loc[i, 'position'] = 1
                result_df.loc[i, 'entry_price'] = current_price
                position = 1
                entry_timestamp = current_time
                entry_price = current_price
                entry_index = i
                
        elif position == 1:
            # Calcular retorno actual
            current_return = (current_price - entry_price) / entry_price
            time_diff = (current_time - entry_timestamp).total_seconds() / 60
            periods_passed = i - entry_index if entry_index is not None else 0
            
            # Verificar condiciones de salida
            exit_triggered = False
            exit_reason = ''
            
            # 1. Stop Loss
            if current_return <= stop_loss:
                exit_triggered = True
                exit_reason = 'stop_loss'
                
            # 2. Take Profit
            elif current_return >= take_profit:
                exit_triggered = True
                exit_reason = 'take_profit'
                
            # 3. Salida por tiempo
            elif periods_passed >= exit_periods:
                exit_triggered = True
                exit_reason = 'time_exit'
                
            # 4. Salida obligatoria al final del día
            elif current_time.hour >= 16 and current_time.minute >= 55:
                exit_triggered = True
                exit_reason = 'end_of_day'
            
            if exit_triggered:
                result_df.loc[i, 'sell_signal'] = True
                result_df.loc[i, 'position'] = 0
                result_df.loc[i, 'entry_price'] = entry_price
                result_df.loc[i, 'exit_price'] = current_price
                result_df.loc[i, 'exit_reason'] = exit_reason
                position = 0
                entry_timestamp = None
                entry_price = 0
                entry_index = None
            else:
                result_df.loc[i, 'position'] = 1
                result_df.loc[i, 'entry_price'] = entry_price
    
    return result_df


def volume_breakout_15min_strategy(df: pd.DataFrame, volume_multiplier: float = 1.5, 
                           trend_window: int = 3, exit_periods: int = 12,
                           stop_loss: float = -0.005, take_profit: float = 0.02) -> pd.DataFrame:
    """
    Estrategia de trading basada en breakout de volumen y tendencia alcista (agregación 15 min)
    TRADES DIARIOS: Cierra automáticamente todas las posiciones activas a las 15:55
    
    Args:
        df: DataFrame con datos de 5 minutos
        volume_multiplier: Multiplicador para determinar volumen alto (1.5 = 50% superior a la media)
        trend_window: Ventana para detectar tendencia alcista
        exit_periods: Número de períodos (de 5 min) para mantener la posición
        stop_loss: Porcentaje de pérdida para salir (-0.005 = -0.5%)
        take_profit: Porcentaje de ganancia para salir (0.02 = +2%)
    
    Returns:
        DataFrame con señales de trading
    """
    # Preparar datos de 5 minutos
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Agregar volumen a 15 minutos para generar señales
    df_15min = aggregate_volume_15min(df)
    df_15min['volume_threshold'] = calculate_volume_threshold(df_15min['volume'], volume_multiplier)
    df_15min['high_volume'] = df_15min['volume'] > df_15min['volume_threshold']
    df_15min['uptrend'] = df_15min['close'].rolling(window=trend_window).apply(
        lambda x: detect_uptrend(x, trend_window), raw=False
    ).fillna(False).astype(bool)
    df_15min['buy_condition'] = df_15min['high_volume'] & df_15min['uptrend']
    
    # Mapear señales de 15 min a datos de 5 min
    buy_signals = pd.Series(False, index=df.index)
    for i, row in df.iterrows():
        time_15min = row['timestamp'].floor('15min')
        signal_row = df_15min[df_15min['timestamp'] == time_15min]
        if not signal_row.empty:
            buy_signals.loc[i] = signal_row.iloc[0]['buy_condition']
    
    # Ejecutar estrategia usando función base común
    return _execute_volume_strategy(df, buy_signals, trend_window, exit_periods, stop_loss, take_profit)


def volume_breakout_5min_strategy(df: pd.DataFrame, volume_multiplier: float = 1.5, 
                                 trend_window: int = 3, exit_periods: int = 12,
                                 stop_loss: float = -0.005, take_profit: float = 0.02,
                                 volume_window: int = 20) -> pd.DataFrame:
    """
    Estrategia de trading basada en breakout de volumen y tendencia alcista
    trabajando directamente sobre velas de 5 minutos (sin agregaciones)
    TRADES DIARIOS: Cierra automáticamente todas las posiciones activas a las 16:55
    
    Args:
        df: DataFrame con datos de 5 minutos
        volume_multiplier: Multiplicador para determinar volumen alto (1.5 = 50% superior a la media)
        trend_window: Ventana para detectar tendencia alcista
        exit_periods: Número de períodos (de 5 min) para mantener la posición
        stop_loss: Porcentaje de pérdida para salir (-0.005 = -0.5%)
        take_profit: Porcentaje de ganancia para salir (0.02 = +2%)
        volume_window: Ventana para calcular la media móvil del volumen
    
    Returns:
        DataFrame con señales de trading
    """
    # Preparar datos de 5 minutos
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calcular señales de compra directamente en datos de 5 minutos
    df['volume_ma'] = df['volume'].rolling(window=volume_window, min_periods=10).mean()
    df['volume_threshold'] = df['volume_ma'] * volume_multiplier
    df['high_volume'] = df['volume'] > df['volume_threshold']
    df['uptrend'] = df['close'].rolling(window=trend_window).apply(
        lambda x: detect_uptrend(x, trend_window), raw=False
    ).fillna(False).astype(bool)
    buy_signals = df['high_volume'] & df['uptrend']
    
    # Ejecutar estrategia usando función base común
    return _execute_volume_strategy(df, buy_signals, trend_window, exit_periods, stop_loss, take_profit)