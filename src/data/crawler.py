"""뉴스 크롤러 (네이버 금융)"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from ..logger import get_logger

logger = get_logger(__name__)

class NewsCrawler:
    """네이버 금융 뉴스 크롤러"""
    
    BASE_URL = "https://finance.naver.com/news/mainnews.naver"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def fetch_headlines(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        주요 뉴스 헤드라인 수집
        
        Returns:
            List[Dict]: [{'title': str, 'link': str, 'summary': str}, ...]
        """
        try:
            response = requests.get(self.BASE_URL, headers=self.headers)
            response.raise_for_status()
            
            # 인코딩 설정 (EUC-KR -> UTF-8)
            response.encoding = 'EUC-KR'
            
            soup = BeautifulSoup(response.text, 'lxml')
            news_list = []
            
            # 주요 뉴스 섹션 파싱
            articles = soup.select('.mainNewsList li')
            
            for article in articles[:limit]:
                title_tag = article.select_one('dt.articleSubject a')
                summary_tag = article.select_one('dd.articleSummary')
                
                if title_tag:
                    title = title_tag.text.strip()
                    link = "https://finance.naver.com" + title_tag['href']
                    summary = summary_tag.text.strip() if summary_tag else ""
                    
                    # 요약문에서 언론사 정보 제거
                    if summary:
                        summary = summary.split('\n')[0]
                        
                    news_list.append({
                        'title': title,
                        'link': link,
                        'summary': summary
                    })
                    
            logger.info(f"Fetched {len(news_list)} news headlines")
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to crawl news: {e}")
            return []

if __name__ == "__main__":
    # 테스트 코드
    from ..logger import setup_logging
    setup_logging()
    
    crawler = NewsCrawler()
    news = crawler.fetch_headlines()
    for n in news:
        print(f"- {n['title']}")
