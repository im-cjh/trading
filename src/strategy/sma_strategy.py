"""SMA (Simple Moving Average) 크로스 전략"""
import pandas as pd
import ta
from .base import BaseStrategy
from ..logger import get_logger

logger = get_logger(__name__)

class SMAStrategy(BaseStrategy):
    """
    이동평균선 크로스 전략
    - 골든크로스 (단기 > 장기): 매수
    - 데드크로스 (단기 < 장기): 매도
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.short_window = self.config.get('short_window', 5)
        self.long_window = self.config.get('long_window', 20)
        
        self.price_buffer = []
        self.min_periods = self.long_window + 1
        self.prev_diff = None  # 이전 (단기 - 장기) 차이
        
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
        
        # SMA 계산
        sma_short = ta.trend.SMAIndicator(close=df['close'], window=self.short_window).sma_indicator().iloc[-1]
        sma_long = ta.trend.SMAIndicator(close=df['close'], window=self.long_window).sma_indicator().iloc[-1]
        
        current_diff = sma_short - sma_long
        
        signal = 'HOLD'
        
        # 크로스 감지
        if self.prev_diff is not None:
            if self.prev_diff < 0 and current_diff > 0:
                logger.info(f"Golden Cross! (Short: {sma_short:.2f} > Long: {sma_long:.2f})")
                signal = 'BUY'
            elif self.prev_diff > 0 and current_diff < 0:
                logger.info(f"Dead Cross! (Short: {sma_short:.2f} < Long: {sma_long:.2f})")
                signal = 'SELL'
                
        self.prev_diff = current_diff
        return signal
