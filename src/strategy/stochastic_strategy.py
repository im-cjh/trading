"""스토캐스틱 전략"""
import pandas as pd
import ta
from .base import BaseStrategy
from ..logger import get_logger

logger = get_logger(__name__)

class StochasticStrategy(BaseStrategy):
    """
    스토캐스틱 오실레이터 전략
    - %K, %D 모두 20 이하 (과매도): 매수
    - %K, %D 모두 80 이상 (과매수): 매도
    """
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.window = self.config.get('window', 14)
        self.smooth_window = self.config.get('smooth_window', 3)
        
        self.price_buffer = [] # (high, low, close) 튜플 저장 필요하지만, 간단히 close만으로 가정하거나 더미 데이터 생성
        # 실제로는 OHLC 데이터가 필요함. 현재 구조상 close만 들어오므로, 
        # 약식으로 high=low=close로 가정하고 계산 (정확도는 떨어짐)
        
        self.min_periods = self.window + self.smooth_window + 1
        
    def analyze(self, market_data: dict) -> str:
        current_price = market_data.get('current_price')
        if current_price is None:
            return 'HOLD'
            
        # 약식 구현: High/Low 정보가 없으므로 Close 가격만 사용
        # 실제 환경에서는 market_data에 high, low가 포함되어야 함
        self.price_buffer.append(current_price)
        
        if len(self.price_buffer) > 100:
            self.price_buffer.pop(0)
            
        if len(self.price_buffer) < self.min_periods:
            return 'HOLD'
            
        df = pd.DataFrame(self.price_buffer, columns=['close'])
        df['high'] = df['close'] # 임시
        df['low'] = df['close']  # 임시
        
        # 스토캐스틱 계산
        stoch = ta.momentum.StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.window,
            smooth_window=self.smooth_window
        )
        
        k = stoch.stoch().iloc[-1]
        d = stoch.stoch_signal().iloc[-1]
        
        if k < 20 and d < 20:
            logger.info(f"Stochastic Oversold! (K:{k:.2f}, D:{d:.2f})")
            return 'BUY'
        elif k > 80 and d > 80:
            logger.info(f"Stochastic Overbought! (K:{k:.2f}, D:{d:.2f})")
            return 'SELL'
            
        return 'HOLD'
