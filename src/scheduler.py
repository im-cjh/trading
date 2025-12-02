"""스케줄러 (자동 리밸런싱 및 파라미터 최적화)"""
import asyncio
import time
from datetime import datetime
from pathlib import Path
from .logger import get_logger
from .universe.selector import UniverseSelector

logger = get_logger(__name__)

class Scheduler:
    """
    정기 작업 스케줄러
    - 주간 리밸런싱 (종목 선정)
    - 주간 파라미터 최적화 (전략 튜닝)
    - 일간 리포트 생성 (예정)
    """
    
    def __init__(self, enable_optimization: bool = True):
        self.selector = UniverseSelector()
        self.running = False
        self.enable_optimization = enable_optimization
        self.last_optimization_date = None
        
    async def start(self):
        """스케줄러 시작"""
        self.running = True
        logger.info("Scheduler started. Monitoring for rebalancing and optimization time...")
        
        while self.running:
            try:
                now = datetime.now()
                
                # 1. 주간 리밸런싱 체크
                # if self.selector.should_rebalance():
                # 테스트를 위해 조건문 주석 처리 및 바로 실행
                if True:
                    logger.info(">>> Weekly Rebalancing Triggered! (TEST MODE) <<<")
                    self.selector.select_stocks(top_n=15)
                    
                    # 중복 실행 방지를 위해 1시간 대기 (또는 충분한 시간 대기)
                    logger.info("Rebalancing complete. Waiting for next cycle...")
                    await asyncio.sleep(3600) 
                
                # 2. 주간 파라미터 최적화 체크 (매주 일요일 02:00)
                if self.enable_optimization and self._should_optimize(now):
                    logger.info(">>> Weekly Parameter Optimization Triggered! <<<")
                    await self._run_optimization()
                    self.last_optimization_date = now.date()
                    logger.info("Parameter optimization complete.")
                
                # 1분마다 체크
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    def _should_optimize(self, now: datetime) -> bool:
        """
        파라미터 최적화 실행 여부 확인
        매주 일요일 02:00에 실행
        """
        # 이미 오늘 실행했으면 스킵
        if self.last_optimization_date == now.date():
            return False
        
        # 일요일(6)이고 02:00~03:00 사이
        if now.weekday() == 6 and now.hour == 2:
            return True
        
        return False
    
    async def _run_optimization(self):
        """파라미터 최적화 실행"""
        try:
            from .optimization import BayesianOptimizer
            from .strategy.rsi_strategy import RSIStrategy
            from .strategy.sma_strategy import SMAStrategy
            from .strategy.bollinger_strategy import BollingerStrategy
            from .strategy.macd_strategy import MACDStrategy
            from .strategy.stochastic_strategy import StochasticStrategy
            import json
            
            # 현재 watchlist에서 종목 가져오기
            watchlist_path = Path(__file__).parent.parent / "config" / "watchlist.json"
            
            if watchlist_path.exists():
                with open(watchlist_path, 'r', encoding='utf-8') as f:
                    watchlist = json.load(f)
                stock_codes = [stock['code'] for stock in watchlist.get('stocks', [])][:3]  # 상위 3종목만
            else:
                # 기본 종목
                stock_codes = ["005930", "000660", "035420"]
            
            logger.info(f"Optimizing for stocks: {stock_codes}")
            
            # 전략 설정
            strategy_configs = [
                {
                    'class': RSIStrategy,
                    'param_bounds': {
                        'rsi_period': (10, 20),
                        'buy_threshold': (20, 35),
                        'sell_threshold': (65, 80)
                    }
                },
                {
                    'class': SMAStrategy,
                    'param_bounds': {
                        'short_window': (3, 10),
                        'long_window': (15, 30)
                    }
                },
                {
                    'class': BollingerStrategy,
                    'param_bounds': {
                        'window': (15, 25),
                        'num_std': (1.5, 2.5)
                    }
                },
                {
                    'class': MACDStrategy,
                    'param_bounds': {
                        'fast_period': (8, 15),
                        'slow_period': (20, 30),
                        'signal_period': (7, 12)
                    }
                },
                {
                    'class': StochasticStrategy,
                    'param_bounds': {
                        'k_period': (10, 18),
                        'd_period': (2, 5),
                        'buy_threshold': (15, 25),
                        'sell_threshold': (75, 85)
                    }
                }
            ]
            
            # 최적화 실행
            save_path = Path(__file__).parent.parent / "data" / "optimization_results"
            save_path.mkdir(parents=True, exist_ok=True)
            
            optimizer = BayesianOptimizer()
            results = optimizer.optimize_multiple_strategies(
                strategy_configs=strategy_configs,
                stock_codes=stock_codes,
                n_iterations=30,  # 주간 최적화는 30회로 제한 (시간 절약)
                save_path=str(save_path)
            )
            
            # 최적화된 파라미터 자동 적용
            from scripts.apply_optimized_params import load_optimized_params, save_config
            params = load_optimized_params(str(save_path))
            if params:
                save_config(params)
                logger.info("Optimized parameters have been automatically applied!")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)

    def stop(self):
        self.running = False
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    from .logger import setup_logging
    setup_logging()
    
    scheduler = Scheduler()
    try:
        asyncio.run(scheduler.start())
    except KeyboardInterrupt:
        pass
