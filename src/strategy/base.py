"""전략 기본 클래스"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    """모든 전략의 기본이 되는 추상 클래스"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> str:
        """
        시장 데이터를 분석하여 매매 신호를 생성
        
        Args:
            market_data: 시장 데이터 (가격, 거래량 등)
            
        Returns:
            str: 'BUY', 'SELL', 'HOLD' 중 하나
        """
        pass
