"""주문 실행 엔진"""
import asyncio
from typing import Optional
from ..api import KISAPIClient, OrderRequest, OrderResponse, AccountBalance, Position
from .mock_executor import MockExecutor
from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


class OrderExecutor:
    """주문 실행 엔진 (모의투자/실거래 자동 전환)"""
    
    def __init__(self, mode: Optional[str] = None):
        """
        Args:
            mode: 'mock' 또는 'real'. None이면 설정 파일에서 읽음
        """
        self.config = get_config()
        self.mode = mode or self.config.get_trading_mode()
        
        # 모의투자/실거래 실행기 초기화
        if self.mode == 'mock':
            initial_cash = self.config.get('execution.mock.initial_cash', 10000000)
            self.executor = MockExecutor(initial_cash=initial_cash)
            logger.info(f"OrderExecutor initialized in MOCK mode with {initial_cash:,}원")
        else:
            self.executor = KISAPIClient(mode='real')
            logger.info("OrderExecutor initialized in REAL mode")
        
        # 주문 제한 설정
        self.max_retries = self.config.get('api.max_retries', 3)
    
    def validate_order(self, order: OrderRequest) -> tuple[bool, str]:
        """주문 유효성 검사
        
        Args:
            order: 주문 요청
        
        Returns:
            (검증 통과 여부, 메시지)
        """
        # 가격 검증
        if order.price < 0:
            return False, "주문가격은 0 이상이어야 합니다"
        
        # 수량 검증
        if order.quantity <= 0:
            return False, "주문수량은 0보다 커야 합니다"
        
        # 종목코드 검증
        if not order.stock_code or len(order.stock_code) != 6:
            return False, "종목코드는 6자리여야 합니다"
        
        # 주문 유형 검증
        if order.order_type.lower() not in ['buy', 'sell']:
            return False, "주문유형은 'buy' 또는 'sell'이어야 합니다"
        
        return True, "OK"
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """주문 실행
        
        Args:
            order: 주문 요청
        
        Returns:
            주문 응답
        """
        # 유효성 검사
        is_valid, message = self.validate_order(order)
        if not is_valid:
            logger.error(f"Order validation failed: {message}")
            return OrderResponse(
                order_id="ERROR",
                stock_code=order.stock_code,
                order_type=order.order_type,
                price=order.price,
                quantity=order.quantity,
                status="rejected",
                message=message
            )
        
        logger.info(f"Placing order: {order.order_type.upper()} {order.stock_code} "
                   f"{order.quantity}주 @ {order.price if order.price > 0 else '시장가'}원")
        
        # 실행
        try:
            if isinstance(self.executor, MockExecutor):
                # 모의투자 (동기)
                response = self.executor.place_order(order)
            else:
                # 실거래 (비동기 래핑)
                response = await asyncio.to_thread(self.executor.place_order, order)
            
            logger.info(f"Order {response.status}: {response.order_id}")
            return response
        
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return OrderResponse(
                order_id="ERROR",
                stock_code=order.stock_code,
                order_type=order.order_type,
                price=order.price,
                quantity=order.quantity,
                status="error",
                message=str(e)
            )
    
    async def get_account_balance(self) -> AccountBalance:
        """계좌 잔고 조회"""
        if isinstance(self.executor, MockExecutor):
            return self.executor.get_account_balance()
        else:
            return await asyncio.to_thread(self.executor.get_account_balance)
    
    async def get_positions(self) -> list[Position]:
        """보유 포지션 조회"""
        if isinstance(self.executor, MockExecutor):
            return self.executor.get_positions()
        else:
            return await asyncio.to_thread(self.executor.get_positions)
    
    def update_price(self, stock_code: str, price: int):
        """현재가 업데이트 (모의투자 전용)
        
        Args:
            stock_code: 종목코드
            price: 현재가
        """
        if isinstance(self.executor, MockExecutor):
            self.executor.update_price(stock_code, price)
    
    def reset(self):
        """계좌 초기화 (모의투자 전용)"""
        if isinstance(self.executor, MockExecutor):
            self.executor.reset()
            logger.info("Mock account reset")
