"""모의투자 주문 실행 시뮬레이터"""
from typing import Dict, List
from datetime import datetime
from ..api.kis_models import OrderRequest, OrderResponse, AccountBalance, Position
from ..logger import get_logger

logger = get_logger(__name__)


class MockExecutor:
    """모의투자 주문 실행 시뮬레이터 (백테스팅용)"""
    
    def __init__(self, initial_cash: int = 10000000):
        """
        Args:
            initial_cash: 초기 현금 (기본 1천만원)
        """
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.orders: List[OrderResponse] = []
        self.order_counter = 1
        
        # 현재 시세 캐시 (실시간 업데이트 필요)
        self.current_prices: Dict[str, int] = {}
        
        logger.info(f"MockExecutor initialized with {initial_cash:,}원")
    
    def update_price(self, stock_code: str, price: int):
        """종목 현재가 업데이트
        
        Args:
            stock_code: 종목코드
            price: 현재가
        """
        self.current_prices[stock_code] = price
    
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """주문 실행 (시뮬레이션)
        
        Args:
            order: 주문 요청
        
        Returns:
            주문 응답
        """
        # 현재가 가져오기 (없으면 주문가로 사용)
        current_price = self.current_prices.get(order.stock_code, order.price)
        if order.price == 0:  # 시장가
            execution_price = current_price
        else:  # 지정가
            execution_price = order.price
        
        # 매수 처리
        if order.order_type.lower() == 'buy':
            total_cost = execution_price * order.quantity
            
            if total_cost > self.cash:
                logger.warning(f"Insufficient cash: need {total_cost:,}, have {self.cash:,}")
                return OrderResponse(
                    order_id=f"MOCK{self.order_counter:06d}",
                    stock_code=order.stock_code,
                    order_type=order.order_type,
                    price=execution_price,
                    quantity=order.quantity,
                    status="rejected",
                    message="잔고 부족"
                )
            
            # 현금 차감
            self.cash -= total_cost
            
            # 포지션 업데이트
            if order.stock_code in self.positions:
                # 기존 포지션에 추가
                pos = self.positions[order.stock_code]
                new_quantity = pos.quantity + order.quantity
                new_avg_price = int(
                    (pos.avg_price * pos.quantity + execution_price * order.quantity) / new_quantity
                )
                pos.quantity = new_quantity
                pos.avg_price = new_avg_price
                pos.current_price = current_price
            else:
                # 새 포지션
                self.positions[order.stock_code] = Position(
                    stock_code=order.stock_code,
                    stock_name=order.stock_code,  # 간단히 코드로 대체
                    quantity=order.quantity,
                    avg_price=execution_price,
                    current_price=current_price
                )
            
            logger.info(f"Buy executed: {order.stock_code} {order.quantity}주 @ {execution_price:,}원")
        
        # 매도 처리
        else:  # sell
            if order.stock_code not in self.positions:
                logger.warning(f"No position to sell: {order.stock_code}")
                return OrderResponse(
                    order_id=f"MOCK{self.order_counter:06d}",
                    stock_code=order.stock_code,
                    order_type=order.order_type,
                    price=execution_price,
                    quantity=order.quantity,
                    status="rejected",
                    message="보유 수량 없음"
                )
            
            pos = self.positions[order.stock_code]
            if pos.quantity < order.quantity:
                logger.warning(f"Insufficient quantity: have {pos.quantity}, trying to sell {order.quantity}")
                return OrderResponse(
                    order_id=f"MOCK{self.order_counter:06d}",
                    stock_code=order.stock_code,
                    order_type=order.order_type,
                    price=execution_price,
                    quantity=order.quantity,
                    status="rejected",
                    message="보유 수량 부족"
                )
            
            # 현금 증가
            total_proceeds = execution_price * order.quantity
            self.cash += total_proceeds
            
            # 포지션 업데이트
            pos.quantity -= order.quantity
            if pos.quantity == 0:
                del self.positions[order.stock_code]
            
            logger.info(f"Sell executed: {order.stock_code} {order.quantity}주 @ {execution_price:,}원")
        
        # 주문 응답 생성
        self.order_counter += 1
        response = OrderResponse(
            order_id=f"MOCK{self.order_counter:06d}",
            stock_code=order.stock_code,
            order_type=order.order_type,
            price=execution_price,
            quantity=order.quantity,
            status="filled",
            message="체결 완료"
        )
        
        self.orders.append(response)
        return response
    
    def get_account_balance(self) -> AccountBalance:
        """계좌 잔고 조회
        
        Returns:
            계좌 잔고 정보
        """
        # 보유 주식 평가액 계산
        stock_value = sum(
            pos.current_price * pos.quantity
            for pos in self.positions.values()
        )
        
        # 총 자산
        total_asset = self.cash + stock_value
        
        # 평가손익
        profit_loss = total_asset - self.initial_cash
        profit_loss_rate = (profit_loss / self.initial_cash) * 100 if self.initial_cash > 0 else 0
        
        return AccountBalance(
            total_asset=total_asset,
            cash=self.cash,
            stock_value=stock_value,
            profit_loss=profit_loss,
            profit_loss_rate=profit_loss_rate
        )
    
    def get_positions(self) -> List[Position]:
        """보유 포지션 조회
        
        Returns:
            포지션 리스트
        """
        return list(self.positions.values())
    
    def reset(self, initial_cash: int = None):
        """계좌 초기화
        
        Args:
            initial_cash: 초기 현금 (None이면 기존 값 사용)
        """
        if initial_cash is not None:
            self.initial_cash = initial_cash
        
        self.cash = self.initial_cash
        self.positions.clear()
        self.orders.clear()
        self.order_counter = 1
        self.current_prices.clear()
        
        logger.info(f"MockExecutor reset with {self.initial_cash:,}원")
