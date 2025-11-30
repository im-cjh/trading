"""스케줄러 (자동 리밸런싱)"""
import asyncio
import time
from datetime import datetime
from .logger import get_logger
from .universe.selector import UniverseSelector

logger = get_logger(__name__)

class Scheduler:
    """
    정기 작업 스케줄러
    - 주간 리밸런싱 (종목 선정)
    - 일간 리포트 생성 (예정)
    """
    
    def __init__(self):
        self.selector = UniverseSelector()
        self.running = False
        
    async def start(self):
        """스케줄러 시작"""
        self.running = True
        logger.info("Scheduler started. Monitoring for rebalancing time...")
        
        while self.running:
            try:
                # 1. 주간 리밸런싱 체크
                # if self.selector.should_rebalance():
                # 테스트를 위해 조건문 주석 처리 및 바로 실행
                if True:
                    logger.info(">>> Weekly Rebalancing Triggered! (TEST MODE) <<<")
                    self.selector.select_stocks(top_n=15)
                    
                    # 중복 실행 방지를 위해 1시간 대기 (또는 충분한 시간 대기)
                    logger.info("Rebalancing complete. Waiting for next cycle...")
                    await asyncio.sleep(3600) 
                
                # 1분마다 체크
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)

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
