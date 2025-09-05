"""
Sistema Principal de Trading - Estrategia de Volumen y Tendencia Alcista
"""
from utils import clean_noisy_data
from trading_strategies import volume_breakout_15min_strategy, volume_breakout_5min_strategy
from backtesting import comprehensive_backtest, analyze_trade_details
from visualization import display_backtest_results, display_trade_analysis, plot_backtest_results, create_performance_dashboard, plot_commission_impact
from config import INTERACTIVE_BROKERS_CONFIG
import pandas as pd


def run_volume_strategy_backtest(data_file='raw_data/2024_data.csv', initial_capital=10000):
    """
    Ejecuta el backtesting completo de la estrategia de volumen
    
    Args:
        data_file: Archivo de datos a analizar
        initial_capital: Capital inicial para el backtesting
    
    Returns:
        tuple: (results, equity_curve, metrics)
    """
    # Cargar y limpiar datos
    print("📊 Cargando datos...")
    df = pd.DataFrame()
    for i in range(4, 5):
        df = pd.concat([df, pd.read_csv(f'labelled_data/202{i}_labelled_data.csv')])
    df = clean_noisy_data(df)
    print(f"   • Datos cargados: {len(df)} registros")
    print(f"   • Período: {df['timestamp'].min()} a {df['timestamp'].max()}")
    
    # Parámetros de la estrategia
    strategy_params = {
        'volume_multiplier': 1.5,   # Volumen 50% superior a la media
        'trend_window': 2,          # Ventana para detectar tendencia alcista  
        'exit_periods': 12,         # Salir después de 60 minutos (12 * 5min)
        'stop_loss': -0.0025,       # Stop loss a -0.25%
        'take_profit': 0.015        # Take profit a +1.5%
    }
    
    # Ejecutar backtesting con comisiones de Interactive Brokers
    print("\n🔄 Ejecutando backtesting con comisiones de Interactive Brokers...")
    print(f"   • Comisión por operación: {INTERACTIVE_BROKERS_CONFIG['commission_rate']:.3%}")
    print(f"   • Comisión mínima: ${INTERACTIVE_BROKERS_CONFIG['minimum_commission']:.2f}")
    
    results, equity_curve, metrics = comprehensive_backtest(
        df, 
        volume_breakout_15min_strategy, 
        strategy_params, 
        initial_capital,
        commission_rate=INTERACTIVE_BROKERS_CONFIG['commission_rate'],
        min_commission=INTERACTIVE_BROKERS_CONFIG['minimum_commission'],
        max_commission=INTERACTIVE_BROKERS_CONFIG['maximum_commission']
    )
    
    # Mostrar resultados
    display_backtest_results(metrics, strategy_params, initial_capital)
    
    # Análisis detallado de trades
    trade_details, exit_stats = analyze_trade_details(results)
    display_trade_analysis(trade_details, exit_stats)
    
    return results, equity_curve, metrics


def run_visualization_suite(results, equity_curve, metrics):
    """
    Ejecuta la suite completa de visualizaciones
    """
    print("\n🎨 Generando visualizaciones...")
    
    # Gráficos básicos del backtesting
    # print("   • Gráficos de backtesting...")
    # plot_backtest_results(equity_curve, results)
    
    # Gráfico de impacto de comisiones
    print("   • Análisis de impacto de comisiones...")
    plot_commission_impact(metrics)
    
    # Dashboard completo
    print("   • Dashboard de rendimiento...")
    create_performance_dashboard(equity_curve, results, metrics)


def main():
    """
    Función principal del sistema
    """
    print("=" * 70)
    print("    SISTEMA DE TRADING - ESTRATEGIA DE VOLUMEN Y TENDENCIA ALCISTA")
    print("=" * 70)
    
    # Ejecutar backtesting
    results, equity_curve, metrics = run_volume_strategy_backtest(initial_capital=50000)
    
    # Generar visualizaciones
    run_visualization_suite(results, equity_curve, metrics)
    
    print("\n✅ Análisis completado exitosamente!")
    print("=" * 70)
    
    return results, equity_curve, metrics


if __name__ == '__main__':
    results, equity_curve, metrics = main()