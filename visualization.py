"""
Herramientas de visualización para backtesting y análisis de trading
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def display_backtest_results(metrics, params, initial_capital):
    """
    Muestra los resultados del backtesting de forma profesional
    """
    print("=" * 60)
    print("           REPORTE DE BACKTESTING - ESTRATEGIA DE VOLUMEN")
    print("=" * 60)
    
    print("\n📊 PARÁMETROS DE LA ESTRATEGIA:")
    print(f"   • Multiplicador de Volumen: {params.get('volume_multiplier', 'N/A')}x")
    print(f"   • Ventana de Tendencia: {params.get('trend_window', 'N/A')} períodos")
    print(f"   • Tiempo de Salida: {params.get('exit_periods', 'N/A')} períodos (60 min)")
    print(f"   • Stop Loss: {params.get('stop_loss', 0):.3%}")
    print(f"   • Take Profit: {params.get('take_profit', 0):.1%}")
    
    print(f"\n💰 RENDIMIENTO FINANCIERO:")
    print(f"   • Capital Inicial: ${metrics['initial_capital']:,.2f}")
    print(f"   • Capital Final: ${metrics['final_capital']:,.2f}")
    print(f"   • Retorno Total (Neto): {metrics['total_return']:.2%}")
    if 'gross_total_return' in metrics:
        print(f"   • Retorno Total (Bruto): {metrics['gross_total_return']:.2%}")
    print(f"   • Retorno Anualizado (Neto): {metrics['annualized_return']:.2%}")
    if 'gross_annualized_return' in metrics:
        print(f"   • Retorno Anualizado (Bruto): {metrics['gross_annualized_return']:.2%}")
    
    # Información específica de Interactive Brokers
    if 'total_commissions' in metrics and metrics['total_commissions'] > 0:
        print(f"\n💳 COSTOS DE INTERACTIVE BROKERS:")
        print(f"   • Comisiones Totales: ${metrics['total_commissions']:.2f}")
        print(f"   • Impacto en Rendimiento: {metrics['commission_impact']:.2%}")
        print(f"   • Comisión Promedio por Trade: ${metrics['total_commissions']/max(metrics['total_trades'],1):.2f}")
        print(f"   • Tasa de Comisión: 0.05% por operación (compra/venta)")
    
    print(f"\n📈 MÉTRICAS DE RIESGO:")
    print(f"   • Volatilidad Anualizada: {metrics['volatility']:.2%}")
    print(f"   • Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"   • Drawdown Máximo: {metrics['max_drawdown']:.2%}")
    print(f"   • Calmar Ratio: {metrics['calmar_ratio']:.2f}")
    
    print(f"\n🎯 ESTADÍSTICAS DE TRADING:")
    print(f"   • Número Total de Trades: {metrics['total_trades']}")
    print(f"   • Tasa de Éxito: {metrics['win_rate']:.1%}")
    print(f"   • Ganancia Promedio: {metrics['avg_win']:.3%}")
    print(f"   • Pérdida Promedio: {metrics['avg_loss']:.3%}")
    print(f"   • Profit Factor: {metrics['profit_factor']:.2f}")
    
    print(f"\n📅 PERÍODO DE ANÁLISIS:")
    print(f"   • Duración: {metrics['period_days']} días ({metrics['period_years']:.1f} años)")
    
    print("\n" + "=" * 60)
    
    # Interpretación de métricas
    print("\n📋 INTERPRETACIÓN DE RESULTADOS:")
    if metrics['sharpe_ratio'] > 1.5:
        print("   ✅ Sharpe Ratio EXCELENTE (>1.5) - Muy buena relación riesgo/retorno")
    elif metrics['sharpe_ratio'] > 1.0:
        print("   ✅ Sharpe Ratio BUENO (>1.0) - Buena relación riesgo/retorno")
    else:
        print("   ⚠️  Sharpe Ratio BAJO (<1.0) - Considerar optimización")
    
    if abs(metrics['max_drawdown']) < 0.10:
        print("   ✅ Drawdown Máximo BAJO (<10%) - Riesgo controlado")
    elif abs(metrics['max_drawdown']) < 0.20:
        print("   ⚠️  Drawdown Máximo MODERADO (<20%) - Riesgo aceptable")
    else:
        print("   ❌ Drawdown Máximo ALTO (>20%) - Alto riesgo")
    
    if metrics['win_rate'] > 0.6:
        print("   ✅ Tasa de Éxito ALTA (>60%) - Estrategia consistente")
    elif metrics['win_rate'] > 0.5:
        print("   ✅ Tasa de Éxito BUENA (>50%) - Estrategia viable")
    else:
        print("   ⚠️  Tasa de Éxito BAJA (<50%) - Revisar parámetros")


def display_trade_analysis(trade_details, exit_stats):
    """
    Muestra análisis detallado de los trades
    """
    if not trade_details:
        print("No hay trades completados para analizar.")
        return
    
    returns = [trade['return'] for trade in trade_details]
    
    print("\n=== ANÁLISIS POR RAZÓN DE SALIDA ===")
    for reason, stats in exit_stats.items():
        reason_name = {
            'stop_loss': 'Stop Loss',
            'take_profit': 'Take Profit', 
            'time_exit': 'Salida por Tiempo',
            'end_of_day': 'Salida al Final del Día'
        }[reason]
        print(f"{reason_name}:")
        print(f"  - Trades: {stats['count']} ({stats['count']/len(returns)*100:.1f}%)")
        print(f"  - Retorno promedio: {stats['avg_return']:.3%}")
        print(f"  - Tasa de éxito: {stats['win_rate']:.1%}")


def plot_backtest_results(equity_df, trades_df, start_date=None, end_date=None):
    """
    Grafica los resultados del backtesting
    """
    if start_date:
        equity_df = equity_df[equity_df['timestamp'] >= start_date]
        trades_df = trades_df[trades_df['timestamp'] >= start_date]
    if end_date:
        equity_df = equity_df[equity_df['timestamp'] <= end_date]
        trades_df = trades_df[trades_df['timestamp'] <= end_date]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Curva de Equity
    ax1.plot(equity_df['timestamp'], equity_df['equity'], linewidth=2, color='blue')
    ax1.set_title('Curva de Equity', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Capital ($)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Precio con señales
    ax2.plot(trades_df['timestamp'], trades_df['close'], alpha=0.7, color='black', linewidth=1)
    buy_signals = trades_df[trades_df['buy_signal'] == True]
    sell_signals = trades_df[trades_df['sell_signal'] == True]
    
    ax2.scatter(buy_signals['timestamp'], buy_signals['close'], 
               color='green', marker='^', s=50, label='Compra', zorder=5)
    ax2.scatter(sell_signals['timestamp'], sell_signals['close'], 
               color='red', marker='v', s=50, label='Venta', zorder=5)
    
    ax2.set_title('Señales de Trading', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Precio ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Drawdown
    equity_series = equity_df['equity']
    rolling_max = equity_series.expanding().max()
    drawdown = (equity_series - rolling_max) / rolling_max
    
    ax3.fill_between(equity_df['timestamp'], drawdown, 0, alpha=0.3, color='red')
    ax3.plot(equity_df['timestamp'], drawdown, color='red', linewidth=1)
    ax3.set_title('Drawdown', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Drawdown (%)')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Volumen
    ax4.bar(trades_df['timestamp'], trades_df['volume'], alpha=0.6, width=0.001)
    ax4.set_title('Volumen', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Volumen')
    ax4.set_xlabel('Fecha')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()


def plot_strategy_performance_comparison(results_dict, start_date=None, end_date=None):
    """
    Compara múltiples estrategias en un solo gráfico
    
    Args:
        results_dict: Dict con formato {'strategy_name': (equity_df, trades_df, metrics)}
    """
    plt.figure(figsize=(15, 10))
    
    # Subplot 1: Comparación de curvas de equity
    plt.subplot(2, 1, 1)
    for strategy_name, (equity_df, _, metrics) in results_dict.items():
        if start_date:
            equity_df = equity_df[equity_df['timestamp'] >= start_date]
        if end_date:
            equity_df = equity_df[equity_df['timestamp'] <= end_date]
        
        plt.plot(equity_df['timestamp'], equity_df['equity'], 
                linewidth=2, label=f"{strategy_name} (Ret: {metrics['total_return']:.1%})")
    
    plt.title('Comparación de Estrategias - Curvas de Equity', fontsize=14, fontweight='bold')
    plt.ylabel('Capital ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Comparación de métricas
    plt.subplot(2, 1, 2)
    strategy_names = list(results_dict.keys())
    sharpe_ratios = [results_dict[name][2]['sharpe_ratio'] for name in strategy_names]
    max_drawdowns = [abs(results_dict[name][2]['max_drawdown']) * 100 for name in strategy_names]
    
    x = np.arange(len(strategy_names))
    width = 0.35
    
    plt.bar(x - width/2, sharpe_ratios, width, label='Sharpe Ratio', alpha=0.7)
    plt.bar(x + width/2, max_drawdowns, width, label='Max Drawdown (%)', alpha=0.7)
    
    plt.title('Comparación de Métricas de Riesgo', fontsize=14, fontweight='bold')
    plt.xlabel('Estrategias')
    plt.ylabel('Valor')
    plt.xticks(x, strategy_names, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_commission_impact(metrics):
    """
    Crea un gráfico específico mostrando el impacto de las comisiones
    """
    if 'total_commissions' not in metrics or metrics['total_commissions'] == 0:
        print("No hay datos de comisiones para mostrar.")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico 1: Comparación de retornos
    categories = ['Retorno Bruto', 'Retorno Neto']
    values = [metrics['gross_total_return'] * 100, metrics['total_return'] * 100]
    colors = ['lightgreen', 'darkgreen']
    
    bars = ax1.bar(categories, values, color=colors, alpha=0.8)
    ax1.set_title('Impacto de Comisiones en el Rendimiento', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Retorno (%)')
    ax1.grid(True, alpha=0.3)
    
    # Añadir valores en las barras
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Mostrar diferencia
    commission_impact = (metrics['gross_total_return'] - metrics['total_return']) * 100
    ax1.text(0.5, max(values) * 0.8, f'Impacto: -{commission_impact:.1f}%', 
            ha='center', transform=ax1.transData, fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # Gráfico 2: Desglose de costos
    gross_profit = (metrics['gross_total_return'] * metrics['initial_capital'])
    commission_cost = metrics['total_commissions']
    net_profit = gross_profit - commission_cost
    
    # Solo mostrar valores positivos para el gráfico de pie
    if gross_profit > 0 and commission_cost > 0:
        sizes = [net_profit if net_profit > 0 else 0, commission_cost]
        if net_profit > 0:
            labels = [f'Ganancia Neta\n${net_profit:.2f}', f'Comisiones\n${commission_cost:.2f}']
        else:
            labels = [f'Pérdida Neta\n${abs(net_profit):.2f}', f'Comisiones\n${commission_cost:.2f}']
        colors = ['lightblue' if net_profit > 0 else 'lightcoral', 'orange']
        
        # Filtrar valores negativos para el pie chart
        positive_sizes = [max(0, size) for size in sizes]
        
        if sum(positive_sizes) > 0:
            wedges, texts, autotexts = ax2.pie(positive_sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'fontsize': 10})
            title = 'Distribución: Ganancias vs Comisiones' if net_profit > 0 else 'Impacto de Comisiones en Pérdidas'
            ax2.set_title(title, fontsize=14, fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'Solo Pérdidas\nNo hay ganancias\npara mostrar', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
            ax2.set_title('Análisis de Pérdidas', fontsize=14, fontweight='bold')
    else:
        ax2.text(0.5, 0.5, 'Datos insuficientes\npara análisis', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Análisis de Costos', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def create_performance_dashboard(equity_df, trades_df, metrics):
    """
    Crea un dashboard completo de rendimiento
    """
    fig = plt.figure(figsize=(20, 12))
    
    # Layout del dashboard
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # 1. Curva de Equity (grande)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(equity_df['timestamp'], equity_df['equity'], linewidth=3, color='blue')
    ax1.set_title('Curva de Equity', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Capital ($)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Precio con señales (grande)
    ax2 = fig.add_subplot(gs[0, 2:])
    ax2.plot(trades_df['timestamp'], trades_df['close'], alpha=0.7, color='black', linewidth=1)
    buy_signals = trades_df[trades_df['buy_signal'] == True]
    sell_signals = trades_df[trades_df['sell_signal'] == True]
    
    ax2.scatter(buy_signals['timestamp'], buy_signals['close'], 
               color='green', marker='^', s=30, label='Compra', zorder=5)
    ax2.scatter(sell_signals['timestamp'], sell_signals['close'], 
               color='red', marker='v', s=30, label='Venta', zorder=5)
    
    ax2.set_title('Señales de Trading', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Precio ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Drawdown
    ax3 = fig.add_subplot(gs[1, :2])
    equity_series = equity_df['equity']
    rolling_max = equity_series.expanding().max()
    drawdown = (equity_series - rolling_max) / rolling_max
    
    ax3.fill_between(equity_df['timestamp'], drawdown * 100, 0, alpha=0.3, color='red')
    ax3.plot(equity_df['timestamp'], drawdown * 100, color='red', linewidth=2)
    ax3.set_title('Drawdown', fontsize=16, fontweight='bold')
    ax3.set_ylabel('Drawdown (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Distribución de retornos
    ax4 = fig.add_subplot(gs[1, 2:])
    buy_signals = trades_df[trades_df['buy_signal'] == True]
    sell_signals = trades_df[trades_df['sell_signal'] == True]
    
    trade_returns = []
    for i, buy_row in buy_signals.iterrows():
        matching_sell = sell_signals[sell_signals.index > i].head(1)
        if not matching_sell.empty:
            sell_row = matching_sell.iloc[0]
            trade_return = (sell_row['close'] - buy_row['close']) / buy_row['close'] * 100
            trade_returns.append(trade_return)
    
    if trade_returns:
        ax4.hist(trade_returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax4.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax4.set_title('Distribución de Retornos por Trade', fontsize=16, fontweight='bold')
        ax4.set_xlabel('Retorno (%)')
        ax4.set_ylabel('Frecuencia')
        ax4.grid(True, alpha=0.3)
    
    # 5-8. Métricas clave (pequeñas)
    metrics_data = [
        ('Retorno Total', f"{metrics['total_return']:.1%}", 'green'),
        ('Sharpe Ratio', f"{metrics['sharpe_ratio']:.2f}", 'blue'),
        ('Max Drawdown', f"{metrics['max_drawdown']:.1%}", 'red'),
        ('Win Rate', f"{metrics['win_rate']:.1%}", 'purple')
    ]
    
    for i, (title, value, color) in enumerate(metrics_data):
        ax = fig.add_subplot(gs[2, i])
        ax.text(0.5, 0.5, value, ha='center', va='center', 
               fontsize=24, fontweight='bold', color=color)
        ax.text(0.5, 0.2, title, ha='center', va='center', 
               fontsize=12, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Añadir borde
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(2)
            spine.set_edgecolor('gray')
    
    plt.suptitle('Dashboard de Rendimiento - Estrategia de Volumen', 
                fontsize=20, fontweight='bold', y=0.95)
    plt.show()
