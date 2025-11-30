"""종목 선정 엔진 (Universe Selector)"""
import json
import os
from typing import List, Dict
from datetime import datetime

from ..logger import get_logger
from ..data.crawler import NewsCrawler
from ..analysis.sentiment import SentimentAnalyzer
from ..analysis.fundamentals import FundamentalAnalyzer

logger = get_logger(__name__)

class UniverseSelector:
    """
    자동 종목 선정 엔진
    1. 뉴스 크롤링 & 감성 분석
    2. 펀더멘털/모멘텀 분석
    3. 종합 점수 산출 및 Top-N 선정
    """
    
    def __init__(self):
        self.crawler = NewsCrawler()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.watchlist_path = "config/watchlist.json"
        
    def select_stocks(self, top_n: int = 15) -> List[str]:
        """
        종목 선정 프로세스 실행
        """
        logger.info("Starting Universe Selection Process...")
        
        # 1. 시장 뉴스 분석 (Market Sentiment)
        logger.info("1. Analyzing Market Sentiment...")
        news_list = self.crawler.fetch_headlines(limit=30)
        headlines = [n['title'] for n in news_list]
        sentiments = self.sentiment_analyzer.analyze(headlines)
        
        avg_sentiment = sum(s['score'] for s in sentiments) / len(sentiments) if sentiments else 0
        logger.info(f"Market Sentiment Score: {avg_sentiment:.2f}")
        
        # 2. 종목별 점수 산출
        logger.info("2. Analyzing Individual Stocks...")
        candidates = self.fundamental_analyzer.get_market_cap_rank(limit=30)
        scored_stocks = []
        
        for code in candidates:
            # 펀더멘털/모멘텀 점수 (종합 점수)
            fund_result = self.fundamental_analyzer.analyze_momentum(code)
            momentum_score = fund_result['total_score']
            
            # 뉴스 감성 점수 (보정값)
            # 실제로는 종목별 뉴스 검색이 필요하나, 여기서는 시장 감성 + 랜덤 보정
            import random
            stock_sentiment = avg_sentiment + random.uniform(-0.1, 0.1)
            sentiment_bonus = stock_sentiment * 10 # -10 ~ +10점 보정
            
            final_score = momentum_score + sentiment_bonus
            
            scored_stocks.append({
                'code': code,
                'score': final_score,
                'details': {
                    'momentum_analysis': fund_result,
                    'sentiment_bonus': sentiment_bonus
                }
            })
            
        # 3. 상위 종목 선정
        scored_stocks.sort(key=lambda x: x['score'], reverse=True)
        selected = scored_stocks[:top_n]
        
        logger.info(f"Selected Top {top_n} Stocks:")
        for s in selected:
            logger.info(f" - {s['code']}: {s['score']:.2f} (Momentum: {s['details']['momentum_analysis']['total_score']:.2f})")
            
        # 4. 결과 저장
        self.save_watchlist(selected)
        
        return [s['code'] for s in selected]
        
    def should_rebalance(self) -> bool:
        """
        리밸런싱 시점 확인
        - 매주 월요일 오전 08:00 ~ 09:00 사이
        """
        now = datetime.now()
        # 월요일(0)이고 8시인 경우
        if now.weekday() == 0 and 8 <= now.hour < 9:
            return True
        return False
        
    def save_watchlist(self, stocks: List[Dict]):
        """선정된 종목을 파일로 저장"""
        data = {
            'updated_at': datetime.now().isoformat(),
            'stocks': stocks
        }
        
        os.makedirs(os.path.dirname(self.watchlist_path), exist_ok=True)
        with open(self.watchlist_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Watchlist saved to {self.watchlist_path}")

if __name__ == "__main__":
    from ..logger import setup_logging
    setup_logging()
    
    selector = UniverseSelector()
    selector.select_stocks()
