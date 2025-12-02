"""백테스팅 프레임워크"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from ..logger import get_logger
from ..api import KISAPIClient
from ..strategy.base import BaseStrategy

logger = get_logger(__name__)


class Backtester:
    """
    전략 백테스팅 엔진
    과거 데이터로 전략을 시뮬레이션하여 성과를 측정
    """
    
    def __init__(self, api_client: KISAPIClient = None):
        self.api_client = api_client or KISAPIClient(mode='mock')
        
    def get_historical_data(
        self, 
        stock_code: str, 
        days: int = 90,
        interval: str = 'D'  # D: 일봉, 30: 30분봉
    ) -> pd.DataFrame:
        """
        과거 시장 데이터 조회
        
        Args:
            stock_code: 종목 코드
            days: 조회 일수
            interval: 봉 간격 ('D': 일봉, '30': 30분봉)
            
        Returns:
            DataFrame with columns: ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        try:
            # KIS API를 통해 과거 데이터 조회
            # 실제 구현 시 API 호출 필요
            # 여기서는 Mock 데이터 생성
            logger.info(f"Fetching historical data for {stock_code} ({days} days)")
            
            # Mock 데이터 생성 (실제로는 API 호출)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # 랜덤 워크 기반 가격 생성 (실제 시장 데이터와 유사하게)
            np.random.seed(hash(stock_code) % (2**32))
            base_price = 50000
            returns = np.random.normal(0.001, 0.02, len(dates))
            prices = base_price * np.exp(np.cumsum(returns))
            
            df = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
                'high': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
                'low': prices * (1 + np.random.uniform(-0.02, 0, len(dates))),
                'close': prices,
                'volume': np.random.randint(100000, 1000000, len(dates))
            })
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return pd.DataFrame()
    
    def run_backtest(
        self,
        strategy: BaseStrategy,
        stock_code: str,
        initial_capital: float = 10000000,  # 1000만원
        days: int = 90,
        commission_rate: float = 0.00015  # 0.015% (편도)
    ) -> Dict[str, Any]:
        """
        백테스트 실행
        
        Args:
            strategy: 테스트할 전략 인스턴스
            stock_code: 종목 코드
            initial_capital: 초기 자본
            days: 백테스트 기간 (일)
            commission_rate: 거래 수수료율
            
        Returns:
            백테스트 결과 딕셔너리
        """
        logger.info(f"Starting backtest for {stock_code} with {strategy.__class__.__name__}")
        
        # 과거 데이터 조회
        df = self.get_historical_data(stock_code, days)
        
        if df.empty:
            logger.error("No historical data available")
            return self._empty_result()
        
        # 백테스트 변수 초기화
        cash = initial_capital
        position = 0  # 보유 주식 수
        avg_buy_price = 0
        trades = []
        equity_curve = []
        
        # 각 시점마다 전략 실행
        for idx, row in df.iterrows():
            market_data = {
                'current_price': row['close'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'volume': row['volume']
            }
            
            # 전략 신호 생성
            signal = strategy.analyze(market_data)
            current_price = row['close']
            
            # 신호에 따라 거래 실행
            if signal == 'BUY' and position == 0 and cash > 0:
                # 매수: 가용 현금의 95% 사용
                buy_amount = cash * 0.95
                quantity = int(buy_amount / current_price)
                
                if quantity > 0:
                    cost = quantity * current_price
                    commission = cost * commission_rate
                    total_cost = cost + commission
                    
                    if total_cost <= cash:
                        cash -= total_cost
                        position = quantity
                        avg_buy_price = current_price
                        
                        trades.append({
                            'date': row['date'],
                            'type': 'BUY',
                            'price': current_price,
                            'quantity': quantity,
                            'commission': commission
                        })
                        
                        logger.debug(f"BUY: {quantity} shares at {current_price:,.0f}")
            
            elif signal == 'SELL' and position > 0:
                # 매도
                revenue = position * current_price
                commission = revenue * commission_rate
                net_revenue = revenue - commission
                
                profit = net_revenue - (position * avg_buy_price)
                profit_rate = (profit / (position * avg_buy_price)) * 100
                
                cash += net_revenue
                
                trades.append({
                    'date': row['date'],
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': position,
                    'commission': commission,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
                
                logger.debug(f"SELL: {position} shares at {current_price:,.0f} (P/L: {profit:,.0f}, {profit_rate:.2f}%)")
                
                position = 0
                avg_buy_price = 0
            
            # 현재 자산 가치 계산
            current_equity = cash + (position * current_price if position > 0 else 0)
            equity_curve.append({
                'date': row['date'],
                'equity': current_equity,
                'cash': cash,
                'position_value': position * current_price if position > 0 else 0
            })
        
        # 마지막에 포지션이 남아있으면 청산
        if position > 0:
            final_price = df.iloc[-1]['close']
            revenue = position * final_price
            commission = revenue * commission_rate
            net_revenue = revenue - commission
            
            profit = net_revenue - (position * avg_buy_price)
            profit_rate = (profit / (position * avg_buy_price)) * 100
            
            cash += net_revenue
            
            trades.append({
                'date': df.iloc[-1]['date'],
                'type': 'SELL',
                'price': final_price,
                'quantity': position,
                'commission': commission,
                'profit': profit,
                'profit_rate': profit_rate
            })
            
            position = 0
        
        # 성과 지표 계산
        final_equity = cash
        total_return = ((final_equity - initial_capital) / initial_capital) * 100
        
        # 승률 계산
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        win_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        win_rate = (len(win_trades) / len(sell_trades) * 100) if sell_trades else 0
        
        # MDD (Maximum Drawdown) 계산
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # 샤프 비율 계산 (간단 버전)
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0
        
        result = {
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'total_trades': len(trades),
            'win_trades': len(win_trades),
            'lose_trades': len(sell_trades) - len(win_trades),
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trades': trades,
            'equity_curve': equity_curve
        }
        
        logger.info(f"Backtest completed: Return={total_return:.2f}%, Win Rate={win_rate:.2f}%, MDD={max_drawdown:.2f}%")
        
        return result
    
    def _empty_result(self) -> Dict[str, Any]:
        """빈 결과 반환"""
        return {
            'initial_capital': 0,
            'final_equity': 0,
            'total_return': 0,
            'total_trades': 0,
            'win_trades': 0,
            'lose_trades': 0,
            'win_rate': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'trades': [],
            'equity_curve': []
        }
