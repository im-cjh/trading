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
        logger.info(f"Market hours: {self.config.get('schedule.market_open')} - "
                   f"{self.config.get('schedule.market_close')}")
        
        try:
            while self.running:
                # 현재 시각
                now = datetime.now()
                
                # TODO: 여기에 실제 트레이딩 로직 구현
                # 1. 시장 데이터 수집
                # 2. 특징 계산
                # 3. AI 예측
                # 4. 전략 실행
                # 5. 주문 실행
                # 6. 모니터링
                
                logger.debug(f"System running... {now}")
                
                # 10초마다 루프
                await asyncio.sleep(10)
        
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
