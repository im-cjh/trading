"""MACD 전략"""
import pandas as pd
import ta
from .base import BaseStrategy
from ..logger import get_logger

logger = get_logger(__name__)

class MACDStrategy(BaseStrategy):
    """
    MACD (Moving Average Convergence Divergence) 전략
    - MACD 선이 Signal 선을 상향 돌파: 매수
    - MACD 선이 Signal 선을 하향 돌파: 매도
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.window_slow = self.config.get('window_slow', 26)
        self.window_fast = self.config.get('window_fast', 12)
        self.window_sign = self.config.get('window_sign', 9)
        
        self.price_buffer = []
        self.min_periods = self.window_slow + self.window_sign + 1
        self.prev_diff = None
        
    def analyze(self, market_data: dict) -> str:
        current_price = market_data.get('current_price')
        if current_price is None:
            return 'HOLD'
            
        self.price_buffer.append(current_price)
        if len(self.price_buffer) > 100:
            self.price_buffer.pop(0)
            
        if len(self.price_buffer) < self.min_periods:
            return 'HOLD'
            
        df = pd.DataFrame(self.price_buffer, columns=['close'])
        
        # MACD 계산
        macd = ta.trend.MACD(
            close=df['close'], 
            window_slow=self.window_slow, 
            window_fast=self.window_fast, 
            window_sign=self.window_sign
        )
        
        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]
        
        current_diff = macd_line - signal_line
        
        signal = 'HOLD'
        
        if self.prev_diff is not None:
            if self.prev_diff < 0 and current_diff > 0:
                logger.info(f"MACD Golden Cross! ({macd_line:.2f} > {signal_line:.2f})")
                signal = 'BUY'
            elif self.prev_diff > 0 and current_diff < 0:
                logger.info(f"MACD Dead Cross! ({macd_line:.2f} < {signal_line:.2f})")
                signal = 'SELL'
                
        self.prev_diff = current_diff
        return signal
