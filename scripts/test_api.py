"""KIS API 연결 테스트 스크립트"""
import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger import setup_logging, get_logger
from src.api import KISAPIClient
from src.execution import OrderExecutor

setup_logging()
logger = get_logger(__name__)


async def test_api_connection():
    """API 연결 테스트"""
    logger.info("=" * 60)
    logger.info("KIS API Connection Test")
    logger.info("=" * 60)
    
    # Order Executor 생성 (자동으로 모의투자/실거래 모드 선택)
    executor = OrderExecutor()
    
    logger.info(f"\nCurrent mode: {executor.mode}")
    
    # 계좌 잔고 조회
    try:
        logger.info("\n[1] Testing account balance query...")
        balance = await executor.get_account_balance()
        
        logger.info("✓ Account balance retrieved successfully")
        logger.info(f"  Total Asset: {balance.total_asset:,}원")
        logger.info(f"  Cash: {balance.cash:,}원")
        logger.info(f"  Stock Value: {balance.stock_value:,}원")
        logger.info(f"  P&L: {balance.profit_loss:,}원 ({balance.profit_loss_rate:+.2f}%)")
    except Exception as e:
        logger.error(f"✗ Failed to get account balance: {e}")
        return False
    
    # 보유 포지션 조회
    try:
        logger.info("\n[2] Testing positions query...")
        positions = await executor.get_positions()
        
        logger.info(f"✓ Positions retrieved successfully ({len(positions)} positions)")
        for pos in positions:
            logger.info(f"  {pos.stock_code} ({pos.stock_name}): "
                       f"{pos.quantity}주 @ {pos.current_price:,}원 "
                       f"(P&L: {pos.profit_loss:,}원, {pos.profit_loss_rate:+.2f}%)")
    except Exception as e:
        logger.error(f"✗ Failed to get positions: {e}")
        return False
    
    # 주식 시세 조회 (삼성전자: 005930)
    if executor.mode == 'real' or hasattr(executor.executor, 'get_stock_price'):
        try:
            logger.info("\n[3] Testing stock quote (Samsung Electronics: 005930)...")
            from src.api import KISAPIClient
            api_client = KISAPIClient(mode=executor.mode)
            quote = api_client.get_stock_price("005930")
            
            logger.info("✓ Stock quote retrieved successfully")
            logger.info(f"  {quote.stock_name} ({quote.stock_code})")
            logger.info(f"  Current: {quote.current_price:,}원")
            logger.info(f"  Open: {quote.open_price:,}원")
            logger.info(f"  High: {quote.high_price:,}원")
            logger.info(f"  Low: {quote.low_price:,}원")
            logger.info(f"  Volume: {quote.volume:,}주")
            logger.info(f"  Change: {quote.change_rate:+.2f}%")
        except Exception as e:
            logger.error(f"✗ Failed to get stock quote: {e}")
            return False
    
    logger.info("\n" + "=" * 60)
    logger.info("All tests passed! ✓")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_api_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nTest failed with error: {e}", exc_info=True)
        sys.exit(1)
