"""전략 파라미터 최적화 스크립트"""
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.optimization import BayesianOptimizer, Backtester
from src.strategy.rsi_strategy import RSIStrategy
from src.strategy.sma_strategy import SMAStrategy
from src.strategy.bollinger_strategy import BollingerStrategy
from src.strategy.macd_strategy import MACDStrategy
from src.strategy.stochastic_strategy import StochasticStrategy
from src.logger import setup_logging, get_logger
import json

setup_logging()
logger = get_logger(__name__)


def main():
    """메인 최적화 실행"""
    
    # 최적화 대상 종목 (예시)
    stock_codes = [
        "005930",  # 삼성전자
        "000660",  # SK하이닉스
        "035420",  # NAVER
    ]
    
    # 전략별 파라미터 범위 정의
    strategy_configs = [
        {
            'class': RSIStrategy,
            'param_bounds': {
                'rsi_period': (10, 20),      # RSI 기간: 10~20
                'buy_threshold': (20, 35),   # 매수 임계값: 20~35
                'sell_threshold': (65, 80)   # 매도 임계값: 65~80
            }
        },
        {
            'class': SMAStrategy,
            'param_bounds': {
                'short_window': (3, 10),     # 단기 이평: 3~10
                'long_window': (15, 30)      # 장기 이평: 15~30
            }
        },
        {
            'class': BollingerStrategy,
            'param_bounds': {
                'window': (15, 25),          # 볼린저 기간: 15~25
                'num_std': (1.5, 2.5)        # 표준편차 배수: 1.5~2.5
            }
        },
        {
            'class': MACDStrategy,
            'param_bounds': {
                'fast_period': (8, 15),      # 빠른 EMA: 8~15
                'slow_period': (20, 30),     # 느린 EMA: 20~30
                'signal_period': (7, 12)     # 시그널: 7~12
            }
        },
        {
            'class': StochasticStrategy,
            'param_bounds': {
                'k_period': (10, 18),        # %K 기간: 10~18
                'd_period': (2, 5),          # %D 기간: 2~5
                'buy_threshold': (15, 25),   # 매수 임계값: 15~25
                'sell_threshold': (75, 85)   # 매도 임계값: 75~85
            }
        }
    ]
    
    # 결과 저장 경로
    save_path = project_root / "data" / "optimization_results"
    save_path.mkdir(parents=True, exist_ok=True)
    
    # 최적화 실행
    logger.info("=" * 80)
    logger.info("Starting Strategy Parameter Optimization")
    logger.info("=" * 80)
    
    optimizer = BayesianOptimizer()
    
    results = optimizer.optimize_multiple_strategies(
        strategy_configs=strategy_configs,
        stock_codes=stock_codes,
        n_iterations=30,  # 각 전략당 30회 반복 (빠른 테스트용, 실전에서는 50-100 권장)
        save_path=str(save_path)
    )
    
    # 결과 요약 출력
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS SUMMARY")
    print("=" * 80)
    
    for strategy_name, stock_results in results.items():
        print(f"\n📊 {strategy_name}")
        print("-" * 80)
        
        for stock_code, result in stock_results.items():
            if result:
                backtest = result['backtest_result']
                print(f"  [{stock_code}]")
                print(f"    Best Params: {result['best_params']}")
                print(f"    Return: {backtest['total_return']:>8.2f}%")
                print(f"    Win Rate: {backtest['win_rate']:>6.2f}%")
                print(f"    Sharpe: {backtest['sharpe_ratio']:>8.2f}")
                print(f"    Max DD: {backtest['max_drawdown']:>8.2f}%")
                print(f"    Trades: {backtest['total_trades']:>4}")
            else:
                print(f"  [{stock_code}] - FAILED")
    
    # 최종 결과를 JSON으로 저장
    summary_path = save_path / "optimization_summary.json"
    
    # 요약 데이터 생성
    summary = {}
    for strategy_name, stock_results in results.items():
        summary[strategy_name] = {}
        for stock_code, result in stock_results.items():
            if result:
                summary[strategy_name][stock_code] = {
                    'best_params': result['best_params'],
                    'total_return': result['backtest_result']['total_return'],
                    'win_rate': result['backtest_result']['win_rate'],
                    'sharpe_ratio': result['backtest_result']['sharpe_ratio'],
                    'max_drawdown': result['backtest_result']['max_drawdown']
                }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Summary saved to: {summary_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
