"""KIS API 클라이언트 테스트 스크립트"""
import logging
import sys
from src.api.kis_client import KISAPIClient
from src.logger import setup_logging

# 로깅 설정 (콘솔 출력)
setup_logging()
logger = logging.getLogger("src.api.kis_client")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def test_client():
    print("=" * 60)
    print("KIS API Client 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 클라이언트 초기화 (토큰 로드 시도)
        client = KISAPIClient(mode='mock')
        print("\n✅ 클라이언트 초기화 성공")
        
        # 2. 주식 현재가 조회 (현대차)
        code = "005380"
        print(f"\n[{code}] 현재가 조회 시도...")
        
        quote = client.get_stock_price(code)
        
        print(f"\n✅ 조회 성공!")
        print(f"  종목명: {quote.stock_name}")
        print(f"  현재가: {quote.current_price:,}원")
        print(f"  전일비: {quote.current_price - quote.prev_close:,}원")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client()
