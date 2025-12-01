"""메인 애플리케이션"""
import asyncio
import argparse
import signal
from datetime import datetime

from .logger import setup_logging, get_logger
from .config import get_config
from .database import get_database
from .api import KISAPIClient
from .execution import OrderExecutor
from .strategy.rsi_strategy import RSIStrategy
from .scheduler import Scheduler

# 로깅 설정
setup_logging()
logger = get_logger(__name__)


class TradingSystem:
    """AI 트레이딩 시스템 메인 클래스"""
    
    def __init__(self, mode: str = None):
        """
        Args:
            mode: 'mock' 또는 'real'. None이면 설정 파일에서 읽음
        """
        self.config = get_config()
        self.mode = mode or self.config.get_trading_mode()
        self.running = False
        
        logger.info("=" * 60)
        logger.info(f"AI Trading System Starting in {self.mode.upper()} mode")
        logger.info("=" * 60)
        
        # 컴포넌트 초기화
        self.db = get_database()
        self.api_client = KISAPIClient(mode=self.mode)
        self.order_executor = OrderExecutor(mode=self.mode)
        
        # 전략 초기화 (RSI 전략)
        self.target_codes = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER
        self.strategies = {
            code: RSIStrategy(config={'rsi_period': 2})
            for code in self.target_codes
        }
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """시그널 핸들러 (Ctrl+C 등)"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def initialize(self):
        """시스템 초기화"""
        logger.info("Initializing trading system...")
        
        # 데이터베이스 테이블 생성
        self.db.create_tables()
        logger.info("Database tables ready")
        
        # API 연결 테스트
        try:
            balance = await self.order_executor.get_account_balance()
            logger.info(f"Account Balance: {balance.total_asset:,}원 "
                       f"(Cash: {balance.cash:,}원, Stock: {balance.stock_value:,}원)")
            logger.info(f"P&L: {balance.profit_loss:,}원 ({balance.profit_loss_rate:+.2f}%)")
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
        
        logger.info("System initialized successfully")
    
    async def run(self):
        """메인 실행 루프"""
        self.running = True
        await self.initialize()
        
        logger.info("Trading system started")
        logger.info(f"Mode: {self.mode.upper()}")
        logger.info(f"Target Stocks: {self.target_codes}")
        
        # 스케줄러 초기화
        self.scheduler = Scheduler()
        
        try:
            # 스케줄러 시작 (백그라운드 태스크)
            scheduler_task = asyncio.create_task(self.scheduler.start())
            
            while self.running:
                # 현재 시각
                now = datetime.now()
                
                # Watchlist 업데이트 확인
                try:
                    import json
                    import os
                    watchlist_path = "config/watchlist.json"
                    if os.path.exists(watchlist_path):
                        with open(watchlist_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            stocks_data = data.get('stocks', [])
                            # 딕셔너리 리스트에서 종목코드만 추출
                            new_codes = [stock['code'] if isinstance(stock, dict) else stock 
                                        for stock in stocks_data]
                            # 리스트가 변경되었으면 업데이트
                            if set(new_codes) != set(self.target_codes):
                                logger.info(f"Watchlist updated: {self.target_codes} -> {new_codes}")
                                self.target_codes = new_codes
                                # 새 종목에 대한 전략 인스턴스 생성 (기존 전략 유지/새 전략 추가)
                                for code in self.target_codes:
                                    if code not in self.strategies:
                                        self.strategies[code] = RSIStrategy(config={'rsi_period': 14})
                except Exception as e:
                    logger.error(f"Failed to update watchlist: {e}")

                for code in self.target_codes:
                    try:
                        # 1. 시장 데이터 수집 (현재가)
                        current_price = 70000 # 기본값
                        try:
                            # 동기식 호출 (임시)
                            if hasattr(self.api_client, 'get_stock_price'):
                                quote = self.api_client.get_stock_price(code)
                                current_price = quote.current_price
                        except Exception as e:
                            logger.warning(f"[{code}] Failed to fetch price: {e}. Using dummy data.")
                            import random
                            current_price = 70000 + random.randint(-1000, 1000)

                        #logger.info(f"[{code}] Current Price: {current_price:,}원")

                        # 2. 전략 분석
                        market_data = {'current_price': current_price}
                        strategy = self.strategies[code]
                        signal = strategy.analyze(market_data)
                        
                        # 3. 신호에 따른 주문 실행
                        if signal in ['BUY', 'SELL']:
                            from .api import OrderRequest
                            
                            order = OrderRequest(
                                stock_code=code,
                                order_type=signal,
                                price=0,  # 시장가
                                quantity=1
                            )
                            
                            logger.info(f"[{code}] >>> Sending {signal} Order")
                            await self.order_executor.place_order(order)
                            
                    except Exception as e:
                        logger.error(f"Error processing {code}: {e}")
                    
                    # API 호출 제한을 피하기 위한 딜레이
                    await asyncio.sleep(1.0)
                
                # 1초마다 루프
                await asyncio.sleep(1)
                
            # 메인 루프 종료 시 스케줄러도 종료
            self.scheduler.stop()
            scheduler_task.cancel()
            try:
                await asyncio.wait_for(scheduler_task, timeout=2.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                logger.info("Scheduler task cancelled")
        
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """시스템 종료"""
        logger.info("Shutting down trading system...")
        
        # TODO: 리소스 정리
        # - WebSocket 연결 종료
        # - Kafka 연결 종료
        # - Redis 연결 종료
        # - 실행 중인 작업 취소
        
        logger.info("Trading system shut down complete")


async def main():
    """메인 엔트리 포인트"""
    parser = argparse.ArgumentParser(description='AI Trading System')
    parser.add_argument(
        '--mode',
        choices=['mock', 'real'],
        help='Trading mode: mock or real (default: from config)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (initialize and exit)'
    )
    
    args = parser.parse_args()
    
    system = TradingSystem(mode=args.mode)
    
    if args.test:
        # 테스트 모드: 초기화만 하고 종료
        await system.initialize()
        logger.info("Test mode complete")
    else:
        # 정상 실행
        await system.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
