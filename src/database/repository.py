"""데이터베이스 레포지토리"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import Trade, PositionHistory, Prediction, AccountSnapshot, MarketData
from ..api.kis_models import OrderResponse, Position, AccountBalance
from ..logger import get_logger

logger = get_logger(__name__)


class TradeRepository:
    """거래 내역 레포지토리"""
    
    @staticmethod
    def create(session: Session, order_response: OrderResponse) -> Trade:
        """거래 생성"""
        trade = Trade(
            order_id=order_response.order_id,
            stock_code=order_response.stock_code,
            order_type=order_response.order_type,
            price=order_response.price,
            quantity=order_response.quantity,
            status=order_response.status,
            message=order_response.message,
            filled_at=datetime.now() if order_response.status == 'filled' else None
        )
        session.add(trade)
        session.flush()
        return trade
    
    @staticmethod
    def get_by_stock(session: Session, stock_code: str, limit: int = 100) -> List[Trade]:
        """종목별 거래 내역 조회"""
        return session.query(Trade).filter(
            Trade.stock_code == stock_code
        ).order_by(desc(Trade.created_at)).limit(limit).all()
    
    @staticmethod
    def get_recent(session: Session, limit: int = 100) -> List[Trade]:
        """최근 거래 내역 조회"""
        return session.query(Trade).order_by(
            desc(Trade.created_at)
        ).limit(limit).all()


class PositionRepository:
    """포지션 레포지토리"""
    
    @staticmethod
    def create_snapshot(session: Session, positions: List[Position]):
        """포지션 스냅샷 생성"""
        timestamp = datetime.now()
        
        for pos in positions:
            position_history = PositionHistory(
                stock_code=pos.stock_code,
                stock_name=pos.stock_name,
                quantity=pos.quantity,
                avg_price=pos.avg_price,
                current_price=pos.current_price,
                profit_loss=pos.profit_loss,
                profit_loss_rate=pos.profit_loss_rate,
                timestamp=timestamp
            )
            session.add(position_history)
        
        session.flush()


class PredictionRepository:
    """예측 레포지토리"""
    
    @staticmethod
    def create(session: Session, stock_code: str, prediction_type: str,
               confidence: float, features: str = None, model_version: str = None) -> Prediction:
        """예측 생성"""
        prediction = Prediction(
            stock_code=stock_code,
            model_version=model_version,
            prediction_type=prediction_type,
            confidence=confidence,
            features=features
        )
        session.add(prediction)
        session.flush()
        return prediction
    
    @staticmethod
    def get_recent(session: Session, stock_code: str, limit: int = 10) -> List[Prediction]:
        """최근 예측 조회"""
        return session.query(Prediction).filter(
            Prediction.stock_code == stock_code
        ).order_by(desc(Prediction.timestamp)).limit(limit).all()


class AccountRepository:
    """계좌 레포지토리"""
    
    @staticmethod
    def create_snapshot(session: Session, balance: AccountBalance) -> AccountSnapshot:
        """계좌 스냅샷 생성"""
        snapshot = AccountSnapshot(
            total_asset=balance.total_asset,
            cash=balance.cash,
            stock_value=balance.stock_value,
            profit_loss=balance.profit_loss,
            profit_loss_rate=balance.profit_loss_rate
        )
        session.add(snapshot)
        session.flush()
        return snapshot
    
    @staticmethod
    def get_history(session: Session, days: int = 30) -> List[AccountSnapshot]:
        """계좌 이력 조회"""
        return session.query(AccountSnapshot).order_by(
            desc(AccountSnapshot.timestamp)
        ).limit(days * 24).all()  # 시간당 1개 가정


class MarketDataRepository:
    """시장 데이터 레포지토리"""
    
    @staticmethod
    def create(session: Session, stock_code: str, timeframe: str,
               open_price: int, high: int, low: int, close: int,
               volume: int, timestamp: datetime) -> MarketData:
        """시장 데이터 생성"""
        data = MarketData(
            stock_code=stock_code,
            timeframe=timeframe,
            open_price=open_price,
            high_price=high,
            low_price=low,
            close_price=close,
            volume=volume,
            timestamp=timestamp
        )
        session.add(data)
        session.flush()
        return data
    
    @staticmethod
    def get_ohlcv(session: Session, stock_code: str, timeframe: str,
                   start_date: datetime = None, limit: int = 1000) -> List[MarketData]:
        """OHLCV 데이터 조회"""
        query = session.query(MarketData).filter(
            MarketData.stock_code == stock_code,
            MarketData.timeframe == timeframe
        )
        
        if start_date:
            query = query.filter(MarketData.timestamp >= start_date)
        
        return query.order_by(desc(MarketData.timestamp)).limit(limit).all()
