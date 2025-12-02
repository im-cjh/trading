"""베이지안 최적화 시스템 빠른 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.optimization import BayesianOptimizer, Backtester
from src.strategy.rsi_strategy import RSIStrategy
from src.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def test_backtester():
    """백테스터 테스트"""
    logger.info("=" * 60)
    logger.info("Testing Backtester...")
    logger.info("=" * 60)
    
    backtester = Backtester()
    
    # RSI 전략 테스트
    strategy = RSIStrategy(config={
        'rsi_period': 14,
        'buy_threshold': 30,
        'sell_threshold': 70
    })
    
    result = backtester.run_backtest(
        strategy=strategy,
        stock_code="005930",  # 삼성전자
        days=30,  # 빠른 테스트를 위해 30일만
        initial_capital=10000000
    )
    
    print("\n📊 Backtest Results:")
    print(f"  Initial Capital: {result['initial_capital']:,}원")
    print(f"  Final Equity: {result['final_equity']:,.0f}원")
    print(f"  Total Return: {result['total_return']:.2f}%")
    print(f"  Total Trades: {result['total_trades']}")
    print(f"  Win Rate: {result['win_rate']:.2f}%")
    print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
    
    logger.info("✅ Backtester test passed!")
    return True


def test_optimizer():
    """옵티마이저 테스트 (빠른 버전)"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Bayesian Optimizer (Quick Test)...")
    logger.info("=" * 60)
    
    optimizer = BayesianOptimizer()
    
    # RSI 전략만 빠르게 테스트
    result = optimizer.optimize_strategy(
        strategy_class=RSIStrategy,
        stock_code="005930",
        param_bounds={
            'rsi_period': (12, 16),  # 좁은 범위로 빠른 테스트
            'buy_threshold': (28, 32),
            'sell_threshold': (68, 72)
        },
        n_iterations=5,  # 빠른 테스트를 위해 5회만
        init_points=2,
        save_path=None  # 저장 안 함
    )
    
    print("\n🎯 Optimization Results:")
    print(f"  Best Parameters: {result['best_params']}")
    print(f"  Best Score: {result['best_score']:.4f}")
    print(f"  Backtest Return: {result['backtest_result']['total_return']:.2f}%")
    print(f"  Win Rate: {result['backtest_result']['win_rate']:.2f}%")
    
    logger.info("✅ Optimizer test passed!")
    return True


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("🧪 Bayesian Optimization System - Quick Test")
    print("=" * 60)
    
    try:
        # 1. 백테스터 테스트
        if not test_backtester():
            logger.error("❌ Backtester test failed!")
            return
        
        # 2. 옵티마이저 테스트
        if not test_optimizer():
            logger.error("❌ Optimizer test failed!")
            return
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! System is ready to use.")
        print("=" * 60)
        print("\n📚 Next steps:")
        print("  1. Run full optimization: python scripts/optimize_strategies.py")
        print("  2. View results: python scripts/view_optimization_results.py")
        print("  3. Apply parameters: python scripts/apply_optimized_params.py")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
