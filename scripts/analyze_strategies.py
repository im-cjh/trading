"""전략 성과 분석 스크립트"""
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import func

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_database
from src.database.models import VirtualTrade

def analyze_strategies():
    """가상 매매 기록 분석"""
    db = get_database()
    session = db.get_session()
    
    try:
        # 전략별 통계 쿼리
        # 1. 총 거래 횟수
        # 2. 승률 (이익 거래 수 / 전체 매도 수)
        # 3. 총 수익금
        # 4. 평균 수익률
        
        trades = pd.read_sql(session.query(VirtualTrade).statement, session.bind)
        
        if trades.empty:
            print("No trades found.")
            return

        # 매도(SELL) 거래만 분석 (실현 손익 기준)
        sell_trades = trades[trades['order_type'] == 'SELL']
        
        if sell_trades.empty:
            print("No sell trades found yet.")
            return

        print("\n" + "=" * 60)
        print("Strategy Performance Report")
        print("=" * 60)
        
        # 전략별 그룹화
        stats = sell_trades.groupby('strategy_name').agg({
            'id': 'count',  # 거래 횟수
            'profit_loss': 'sum',  # 총 손익
            'profit_loss_rate': 'mean'  # 평균 수익률
        }).rename(columns={'id': 'Trade Count', 'profit_loss': 'Total P&L', 'profit_loss_rate': 'Avg Return (%)'})
        
        # 승률 계산
        win_rates = []
        for strategy in stats.index:
            strategy_trades = sell_trades[sell_trades['strategy_name'] == strategy]
            win_count = len(strategy_trades[strategy_trades['profit_loss'] > 0])
            total_count = len(strategy_trades)
            win_rate = (win_count / total_count * 100) if total_count > 0 else 0
            win_rates.append(win_rate)
            
        stats['Win Rate (%)'] = win_rates
        
        # 출력 포맷팅
        pd.options.display.float_format = '{:,.2f}'.format
        print(stats)
        print("=" * 60)
        
    except Exception as e:
        print(f"Error analyzing strategies: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    analyze_strategies()
