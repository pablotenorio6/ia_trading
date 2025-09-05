"""
Configuración del sistema de trading
"""

# Configuración de datos
DATA_CONFIG = {
    'raw_data_path': 'raw_data/',
    'labelled_data_path': 'labelled_data/',
    'default_file': '2024_data.csv',
    'timestamp_column': 'timestamp',
    'price_column': 'close',
    'volume_column': 'volume'
}

# Configuración de la estrategia de volumen
VOLUME_STRATEGY_CONFIG = {
    'volume_multiplier': 1.5,      # Multiplicador para volumen alto
    'trend_window': 2,             # Ventana para detectar tendencia
    'exit_periods': 12,            # Períodos para salida por tiempo (60 min)
    'stop_loss': -0.0025,          # Stop loss (-0.25%)
    'take_profit': 0.015,          # Take profit (+1.5%)
    'volume_window': 20,           # Ventana para calcular media de volumen
    'min_periods': 10              # Períodos mínimos para calcular media
}

# Configuración de backtesting
BACKTEST_CONFIG = {
    'initial_capital': 1000,      # Capital inicial
    'commission': 0.0005,          # Comisión Interactive Brokers: 0.05% por operación
    'slippage': 0.0001,           # Slippage estimado (0.01%)
    'risk_free_rate': 0.02,       # Tasa libre de riesgo (2% anual)
    'trading_days_per_year': 252   # Días de trading por año
}

# Configuración específica de Interactive Brokers
INTERACTIVE_BROKERS_CONFIG = {
    'commission_rate': 0.0005,     # 0.05% por operación (compra + venta = 0.1% total por trade)
    'minimum_commission': 1.25,     # Comisión mínima por operación (USD)
    'maximum_commission': 100.0,   # Comisión máxima por operación (USD)
    'currency': 'USD',
    'market': 'SMART',             # Enrutamiento inteligente de órdenes
    'exchange': 'NYSE'             # Bolsa principal
}

# Configuración de visualización
VISUALIZATION_CONFIG = {
    'figure_size': (16, 12),       # Tamaño de figuras
    'dpi': 100,                    # Resolución
    'style': 'seaborn-v0_8',      # Estilo de matplotlib
    'color_palette': {
        'buy_signal': 'green',
        'sell_signal': 'red', 
        'equity_curve': 'blue',
        'drawdown': 'red',
        'volume': 'skyblue'
    }
}

# Configuración de métricas
METRICS_CONFIG = {
    'sharpe_excellent': 1.5,       # Umbral para Sharpe excelente
    'sharpe_good': 1.0,           # Umbral para Sharpe bueno
    'drawdown_low': 0.10,         # Umbral para drawdown bajo
    'drawdown_moderate': 0.20,    # Umbral para drawdown moderado
    'win_rate_high': 0.6,         # Umbral para win rate alto
    'win_rate_good': 0.5          # Umbral para win rate bueno
}

# Configuración de archivos de salida
OUTPUT_CONFIG = {
    'results_path': 'results/',
    'plots_path': 'plots/',
    'reports_path': 'reports/',
    'save_plots': False,           # Guardar gráficos automáticamente
    'save_results': False,         # Guardar resultados automáticamente
    'export_format': 'csv'         # Formato de exportación
}
