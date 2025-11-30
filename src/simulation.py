"""가상 시뮬레이션 엔진"""
import asyncio
import random
from datetime import datetime
from typing import Dict, List

from .logger import get_logger
from .database import get_database
from .database.models import VirtualTrade
from .strategy.base import BaseStrategy
from .strategy.rsi_strategy import RSIStrategy
from .strategy.sma_strategy import SMAStrategy
from .strategy.bollinger_strategy import BollingerStrategy
from .strategy.macd_strategy import MACDStrategy
from .strategy.stochastic_strategy import StochasticStrategy

logger = get_logger(__name__)

class VirtualExecutor:
    """가상 주문 실행기"""
    def __init__(self):
        self.db = get_database()
        # 전략별 포지션 관리: {strategy_name: {stock_code: {'quantity': int, 'avg_price': float}}}
        self.positions = {}
        
    def execute(self, strategy_name: str, stock_code: str, order_type: str, price: int, quantity: int):
        """가상 주문 실행 및 DB 저장"""
        
        # 포지션 정보 초기화
        if strategy_name not in self.positions:
            self.positions[strategy_name] = {}
        if stock_code not in self.positions[strategy_name]:
            self.positions[strategy_name][stock_code] = {'quantity': 0, 'avg_price': 0}
            
        position = self.positions[strategy_name][stock_code]
        profit_loss = 0
        profit_loss_rate = 0.0
        
        if order_type == 'BUY':
            # 매수: 평단가 갱신
            total_cost = (position['quantity'] * position['avg_price']) + (quantity * price)
            total_qty = position['quantity'] + quantity
            position['avg_price'] = total_cost / total_qty
            position['quantity'] = total_qty
            
        elif order_type == 'SELL':
            # 매도: 수익 실현
            if position['quantity'] < quantity:
                logger.warning(f"[{strategy_name}] Not enough quantity to sell {stock_code}")
                return
                
            profit_loss = (price - position['avg_price']) * quantity
            profit_loss_rate = (price - position['avg_price']) / position['avg_price'] * 100
            
            position['quantity'] -= quantity
            if position['quantity'] == 0:
                position['avg_price'] = 0
        
        # DB 저장
        trade = VirtualTrade(
            strategy_name=strategy_name,
            stock_code=stock_code,
            order_type=order_type,
            price=price,
            quantity=quantity,
            profit_loss=profit_loss if order_type == 'SELL' else None,
            profit_loss_rate=profit_loss_rate if order_type == 'SELL' else None,
            timestamp=datetime.now()
        )
        
        session = self.db.get_session()
        try:
            session.add(trade)
            session.commit()
            logger.info(f"[{strategy_name}] {order_type} {stock_code} @ {price} (Qty: {quantity})")
        except Exception as e:
            logger.error(f"Failed to save virtual trade: {e}")
            session.rollback()
        finally:
            session.close()


class SimulationRunner:
    """시뮬레이션 실행기"""
    def __init__(self):
        self.executor = VirtualExecutor()
        self.target_codes = ["005930", "000660", "035420"]
        
        # 5가지 전략 초기화
        self.strategies: Dict[str, BaseStrategy] = {
            "RSI": RSIStrategy(),
            "SMA": SMAStrategy(),
            "Bollinger": BollingerStrategy(),
            "MACD": MACDStrategy(),
            "Stochastic": StochasticStrategy()
        }
        
        self.running = False
        
    async def run(self):
        """시뮬레이션 루프"""
        self.running = True
        logger.info("Starting Multi-Strategy Simulation...")
        
        # DB 테이블 생성 (VirtualTrade 포함)
        db = get_database()
        db.create_tables()
        
        try:
            while self.running:
                for code in self.target_codes:
                    # 가상 가격 생성 (랜덤 워크)
                    # 실제로는 API에서 가져와야 함
                    current_price = 70000 + random.randint(-500, 500)
                    
                    market_data = {'current_price': current_price}
                    
                    # 모든 전략에 동일한 가격 데이터 주입
                    for name, strategy in self.strategies.items():
                        try:
                            signal = strategy.analyze(market_data)
                            
                            if signal == 'BUY':
                                self.executor.execute(name, code, 'BUY', current_price, 1)
                            elif signal == 'SELL':
                                self.executor.execute(name, code, 'SELL', current_price, 1)
                                
                        except Exception as e:
                            logger.error(f"Error in strategy {name}: {e}")
                            
                await asyncio.sleep(1) # 1초 단위 시뮬레이션
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped.")

if __name__ == "__main__":
    from .logger import setup_logging
    setup_logging()
    
    runner = SimulationRunner()
    asyncio.run(runner.run())
