"""
Sistema de backtesting para estrategias de trading
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_commission(trade_value, commission_rate=0.0005, min_commission=1.0, max_commission=100.0):
    """
    Calcula la comisión de Interactive Brokers para una operación
    
    Args:
        trade_value: Valor de la operación en USD
        commission_rate: Tasa de comisión (0.05% = 0.0005)
        min_commission: Comisión mínima por operación
        max_commission: Comisión máxima por operación
    
    Returns:
        float: Comisión a pagar
    """
    commission = trade_value * commission_rate
    return max(min_commission, min(commission, max_commission))


def calculate_equity_curve(df, initial_capital=10000, commission_rate=0.0005, 
                          min_commission=1.25, max_commission=100.0):
    """
    Calcula la curva de equity (capital acumulado) incluyendo comisiones
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Inicializar variables
    equity = [initial_capital]
    capital = initial_capital
    position_size = 0
    shares = 0
    total_commissions = 0
    
    for i, row in df.iterrows():
        if row['buy_signal'] and position_size == 0:
            # Comprar: usar capital disponible menos comisión
            trade_value = capital
            commission = calculate_commission(trade_value, commission_rate, min_commission, max_commission)
            
            # Restar comisión del capital disponible para compra
            available_capital = capital - commission
            shares = available_capital / row['close']
            total_commissions += commission
            position_size = 1
            
        elif row['sell_signal'] and position_size == 1:
            # Vender: convertir shares a capital menos comisión
            trade_value = shares * row['close']
            commission = calculate_commission(trade_value, commission_rate, min_commission, max_commission)
            
            capital = trade_value - commission
            total_commissions += commission
            shares = 0
            position_size = 0
            
        # Calcular equity actual
        if position_size == 1:
            current_equity = shares * row['close']
        else:
            current_equity = capital
            
        equity.append(current_equity)
    
    # Crear DataFrame con equity curve
    equity_df = pd.DataFrame({
        'timestamp': df['timestamp'].tolist() + [df['timestamp'].iloc[-1]],
        'equity': equity,
        'total_commissions': [0] + [total_commissions] * len(df)
    })
    
    return equity_df


def calculate_performance_metrics(equity_df, trades_df):
    """
    Calcula métricas estándar de backtesting incluyendo análisis de comisiones
    """
    # Datos básicos
    initial_equity = equity_df['equity'].iloc[0]
    final_equity = equity_df['equity'].iloc[-1]
    
    # Comisiones totales pagadas
    total_commissions = equity_df['total_commissions'].iloc[-1] if 'total_commissions' in equity_df.columns else 0
    
    # Calcular returns diarios
    equity_df['returns'] = equity_df['equity'].pct_change().fillna(0)
    
    # Trades completados
    buy_signals = trades_df[trades_df['buy_signal'] == True]
    sell_signals = trades_df[trades_df['sell_signal'] == True]
    
    trade_returns = []
    gross_trade_returns = []  # Retornos sin considerar comisiones
    
    for i, buy_row in buy_signals.iterrows():
        matching_sell = sell_signals[sell_signals.index > i].head(1)
        if not matching_sell.empty:
            sell_row = matching_sell.iloc[0]
            # Retorno bruto (sin comisiones)
            gross_return = (sell_row['close'] - buy_row['close']) / buy_row['close']
            gross_trade_returns.append(gross_return)
            
            # Retorno neto estimado (considerando comisiones aproximadas)
            # Comisión total por trade: 0.1% (0.05% compra + 0.05% venta)
            net_return = gross_return - 0.001  # Aproximación de comisiones
            trade_returns.append(net_return)
    
    trade_returns = np.array(trade_returns)
    gross_trade_returns = np.array(gross_trade_returns)
    
    # Métricas de rendimiento
    total_return = (final_equity - initial_equity) / initial_equity
    gross_total_return = total_return + (total_commissions / initial_equity)  # Retorno sin comisiones
    
    # Período de análisis
    start_date = equity_df['timestamp'].iloc[0]
    end_date = equity_df['timestamp'].iloc[-1]
    days = (end_date - start_date).days
    years = days / 365.25
    
    # Rendimiento anualizado
    annualized_return = (final_equity / initial_equity) ** (1/years) - 1 if years > 0 else 0
    gross_annualized_return = ((initial_equity + total_commissions + (final_equity - initial_equity)) / initial_equity) ** (1/years) - 1 if years > 0 else 0
    
    # Volatilidad (desviación estándar de returns diarios anualizada)
    daily_returns = equity_df['returns'].dropna()
    volatility = daily_returns.std() * np.sqrt(252)  # 252 días de trading al año
    
    # Sharpe Ratio (asumiendo risk-free rate = 0)
    sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
    
    # Maximum Drawdown
    equity_series = equity_df['equity']
    rolling_max = equity_series.expanding().max()
    drawdown = (equity_series - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # Calmar Ratio
    calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # Win Rate y Profit Factor
    if len(trade_returns) > 0:
        win_rate = len(trade_returns[trade_returns > 0]) / len(trade_returns)
        winning_trades = trade_returns[trade_returns > 0]
        losing_trades = trade_returns[trade_returns < 0]
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 0
        profit_factor = (avg_win * len(winning_trades)) / (avg_loss * len(losing_trades)) if avg_loss > 0 else float('inf')
        
        # Métricas brutas (sin comisiones)
        gross_win_rate = len(gross_trade_returns[gross_trade_returns > 0]) / len(gross_trade_returns)
        gross_avg_win = gross_trade_returns[gross_trade_returns > 0].mean() if len(gross_trade_returns[gross_trade_returns > 0]) > 0 else 0
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0
        gross_win_rate = 0
        gross_avg_win = 0
    
    return {
        'initial_capital': initial_equity,
        'final_capital': final_equity,
        'total_return': total_return,
        'gross_total_return': gross_total_return,
        'annualized_return': annualized_return,
        'gross_annualized_return': gross_annualized_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar_ratio,
        'total_trades': len(trade_returns),
        'win_rate': win_rate,
        'gross_win_rate': gross_win_rate,
        'avg_win': avg_win,
        'gross_avg_win': gross_avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'total_commissions': total_commissions,
        'commission_impact': (total_commissions / initial_equity),
        'period_days': days,
        'period_years': years
    }


def comprehensive_backtest(df, strategy_func, strategy_params=None, initial_capital=10000, 
                          commission_rate=0.0005, min_commission=1.0, max_commission=100.0):
    """
    Backtesting completo con métricas estándar de la industria incluyendo comisiones
    
    Args:
        df: DataFrame con datos de trading
        strategy_func: Función de estrategia a testear
        strategy_params: Parámetros de la estrategia
        initial_capital: Capital inicial para el backtesting
        commission_rate: Tasa de comisión por operación (Interactive Brokers: 0.05%)
        min_commission: Comisión mínima por operación
        max_commission: Comisión máxima por operación
    
    Returns:
        tuple: (results_df, equity_curve, metrics)
    """
    if strategy_params is None:
        strategy_params = {}
    
    # Ejecutar estrategia
    results = strategy_func(df, **strategy_params)
    
    # Crear serie temporal de equity con comisiones
    equity_curve = calculate_equity_curve(results, initial_capital, 
                                        commission_rate, min_commission, max_commission)
    
    # Calcular métricas de rendimiento
    metrics = calculate_performance_metrics(equity_curve, results)
    
    return results, equity_curve, metrics


def analyze_trade_details(df):
    """
    Analiza los detalles de los trades ejecutados
    """
    buy_signals = df[df['buy_signal'] == True]
    sell_signals = df[df['sell_signal'] == True]
    
    if len(sell_signals) == 0:
        print(f"Se generaron {len(buy_signals)} señales de compra, pero ninguna se cerró aún.")
        return [], {}
    
    # Calcular retornos por trade y razones de salida
    returns = []
    exit_reasons = []
    trade_details = []
    
    for i, buy_row in buy_signals.iterrows():
        # Buscar la señal de venta correspondiente
        matching_sell = sell_signals[sell_signals.index > i].head(1)
        if not matching_sell.empty:
            sell_row = matching_sell.iloc[0]
            entry_price = buy_row['close']
            exit_price = sell_row['close']
            trade_return = (exit_price - entry_price) / entry_price
            exit_reason = sell_row['exit_reason']
            
            returns.append(trade_return)
            exit_reasons.append(exit_reason)
            trade_details.append({
                'entry_time': buy_row['timestamp'],
                'exit_time': sell_row['timestamp'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'return': trade_return,
                'exit_reason': exit_reason
            })
    
    # Análisis por razón de salida
    exit_stats = {}
    for reason in ['stop_loss', 'take_profit', 'time_exit', 'end_of_day']:
        reason_returns = [r for r, er in zip(returns, exit_reasons) if er == reason]
        if reason_returns:
            exit_stats[reason] = {
                'count': len(reason_returns),
                'avg_return': np.mean(reason_returns),
                'win_rate': len([r for r in reason_returns if r > 0]) / len(reason_returns)
            }
    
    return trade_details, exit_stats
