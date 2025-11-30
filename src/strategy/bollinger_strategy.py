"""볼린저 밴드 전략"""
import pandas as pd
import ta
from .base import BaseStrategy
from ..logger import get_logger

logger = get_logger(__name__)

class BollingerStrategy(BaseStrategy):
    """
    볼린저 밴드 평균 회귀 전략
    - 하단 밴드 터치: 매수 (과매도)
    - 상단 밴드 터치: 매도 (과매수)
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.window = self.config.get('window', 20)
        self.window_dev = self.config.get('window_dev', 2.0)
        
        self.price_buffer = []
        self.min_periods = self.window + 1
        
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
        
        # 볼린저 밴드 계산
        indicator = ta.volatility.BollingerBands(close=df['close'], window=self.window, window_dev=self.window_dev)
        
        bb_high = indicator.bollinger_hband().iloc[-1]
        bb_low = indicator.bollinger_lband().iloc[-1]
        
        if current_price <= bb_low:
            logger.info(f"Price hit Lower Band! ({current_price} <= {bb_low:.2f})")
            return 'BUY'
        elif current_price >= bb_high:
            logger.info(f"Price hit Upper Band! ({current_price} >= {bb_high:.2f})")
            return 'SELL'
            
        return 'HOLD'
