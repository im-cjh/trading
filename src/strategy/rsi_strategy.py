"""RSI 기반 매매 전략"""
import pandas as pd
import ta
from .base import BaseStrategy
from ..logger import get_logger

logger = get_logger(__name__)

class RSIStrategy(BaseStrategy):
    """
    RSI(Relative Strength Index) 기반 전략
    - RSI < 30: 과매도 (매수 신호)
    - RSI > 70: 과매수 (매도 신호)
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.buy_threshold = self.config.get('buy_threshold', 30)
        self.sell_threshold = self.config.get('sell_threshold', 70)
        
        # 가격 데이터를 저장할 버퍼 (최소 RSI 계산에 필요한 만큼)
        self.price_buffer = []
        self.min_periods = self.rsi_period + 1
        
    def analyze(self, market_data: dict) -> str:
        """
        RSI 계산 및 신호 생성
        
        Args:
            market_data: {'current_price': float, ...}
        """
        current_price = market_data.get('current_price')
        if current_price is None:
            return 'HOLD'
            
        # 데이터 버퍼에 추가
        self.price_buffer.append(current_price)
        
        # 버퍼 크기 관리 (너무 커지지 않게 유지)
        if len(self.price_buffer) > 100:
            self.price_buffer.pop(0)
            
        # 데이터가 충분하지 않으면 대기
        if len(self.price_buffer) < self.min_periods:
            logger.debug(f"Collecting data... ({len(self.price_buffer)}/{self.min_periods})")
            return 'HOLD'
            
        # RSI 계산
        df = pd.DataFrame(self.price_buffer, columns=['close'])
        rsi_indicator = ta.momentum.RSIIndicator(close=df['close'], window=self.rsi_period)
        current_rsi = rsi_indicator.rsi().iloc[-1]
        
        logger.info(f"RSI Calculated: {current_rsi:.2f}")
        
        # 신호 생성
        if current_rsi <= self.buy_threshold:
            logger.info(f"BUY Signal! (RSI: {current_rsi:.2f} <= {self.buy_threshold})")
            return 'BUY'
            
        elif current_rsi >= self.sell_threshold:
            logger.info(f"SELL Signal! (RSI: {current_rsi:.2f} >= {self.sell_threshold})")
            return 'SELL'
            
        return 'HOLD'
