"""한국투자증권 API 데이터 모델"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """OAuth2 토큰 응답"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    access_token_token_expired: Optional[str] = None


class StockQuote(BaseModel):
    """주식 시세 정보"""
    stock_code: str = Field(..., description="종목코드")
    stock_name: Optional[str] = Field(None, description="종목명")
    current_price: int = Field(..., description="현재가")
    prev_close: int = Field(..., description="전일종가")
    open_price: int = Field(..., description="시가")
    high_price: int = Field(..., description="고가")
    low_price: int = Field(..., description="저가")
    volume: int = Field(..., description="거래량")
    timestamp: datetime = Field(default_factory=datetime.now, description="시간")
    
    @property
    def change_rate(self) -> float:
        """등락률 (%)"""
        if self.prev_close == 0:
            return 0.0
        return ((self.current_price - self.prev_close) / self.prev_close) * 100


class OrderRequest(BaseModel):
    """주문 요청"""
    stock_code: str = Field(..., description="종목코드")
    order_type: str = Field(..., description="주문유형: buy/sell")
    price: int = Field(..., description="주문가격 (0=시장가)")
    quantity: int = Field(..., description="주문수량")
    order_division: str = Field(default="00", description="주문구분")


class OrderResponse(BaseModel):
    """주문 응답"""
    order_id: str = Field(..., description="주문번호")
    stock_code: str
    order_type: str
    price: int
    quantity: int
    status: str = Field(..., description="주문상태")
    message: Optional[str] = None


class AccountBalance(BaseModel):
    """계좌 잔고"""
    total_asset: int = Field(..., description="총 자산")
    cash: int = Field(..., description="현금")
    stock_value: int = Field(..., description="주식 평가액")
    profit_loss: int = Field(..., description="평가손익")
    profit_loss_rate: float = Field(..., description="수익률(%)")


class Position(BaseModel):
    """보유 포지션"""
    stock_code: str
    stock_name: str
    quantity: int = Field(..., description="보유수량")
    avg_price: int = Field(..., description="평균단가")
    current_price: int = Field(..., description="현재가")
    
    @property
    def total_value(self) -> int:
        """평가금액"""
        return self.current_price * self.quantity
    
    @property
    def profit_loss(self) -> int:
        """평가손익"""
        return (self.current_price - self.avg_price) * self.quantity
    
    @property
    def profit_loss_rate(self) -> float:
        """수익률 (%)"""
        if self.avg_price == 0:
            return 0.0
        return ((self.current_price - self.avg_price) / self.avg_price) * 100


class WebSocketMessage(BaseModel):
    """WebSocket 메시지"""
    message_type: str
    stock_code: Optional[str] = None
    data: dict
    timestamp: datetime = Field(default_factory=datetime.now)
