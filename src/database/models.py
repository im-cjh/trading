"""데이터베이스 모델"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Trade(Base):
    """거래 내역"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    stock_code = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))
    order_type = Column(String(10), nullable=False)  # buy/sell
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # submitted/filled/rejected/cancelled
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now, index=True)
    filled_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_stock_created', 'stock_code', 'created_at'),
    )


class PositionHistory(Base):
    """포지션 히스토리"""
    __tablename__ = 'position_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Integer, nullable=False)
    current_price = Column(Integer, nullable=False)
    profit_loss = Column(Integer)
    profit_loss_rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)


class Prediction(Base):
    """AI 예측 로그"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)
    model_version = Column(String(50))
    prediction_type = Column(String(20))  # buy/sell/hold
    confidence = Column(Float)
    features = Column(Text)  # JSON 형태의 특징 데이터
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_stock_timestamp', 'stock_code', 'timestamp'),
    )


class AccountSnapshot(Base):
    """계좌 스냅샷"""
    __tablename__ = 'account_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_asset = Column(Integer, nullable=False)
    cash = Column(Integer, nullable=False)
    stock_value = Column(Integer, nullable=False)
    profit_loss = Column(Integer)
    profit_loss_rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)


class StrategyVersion(Base):
    """전략 버전"""
    __tablename__ = 'strategy_versions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parameters = Column(Text)  # JSON 형태의 파라미터
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    activated_at = Column(DateTime)


class MarketData(Base):
    """시장 데이터 (OHLCV)"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d
    open_price = Column(Integer, nullable=False)
    high_price = Column(Integer, nullable=False)
    low_price = Column(Integer, nullable=False)
    close_price = Column(Integer, nullable=False)
    volume = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_stock_timeframe_timestamp', 'stock_code', 'timeframe', 'timestamp'),
    )


class VirtualTrade(Base):
    """가상 거래 내역 (시뮬레이션용)"""
    __tablename__ = 'virtual_trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String(50), nullable=False, index=True)
    stock_code = Column(String(20), nullable=False, index=True)
    order_type = Column(String(10), nullable=False)  # buy/sell
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    profit_loss = Column(Integer)  # 매도 시 실현 손익
    profit_loss_rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_strategy_stock', 'strategy_name', 'stock_code'),
    )
