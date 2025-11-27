"""한국투자증권 API REST 클라이언트"""
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..config import get_config
from ..logger import get_logger
from .kis_models import (
    TokenResponse, StockQuote, OrderRequest, OrderResponse,
    AccountBalance, Position
)

logger = get_logger(__name__)


class KISAPIClient:
    """한국투자증권 API 클라이언트"""
    
    def __init__(self, mode: Optional[str] = None):
        """
        Args:
            mode: 'mock' 또는 'real'. None이면 설정 파일에서 읽음
        """
        self.config = get_config()
        self.mode = mode or self.config.get_trading_mode()
        self.credentials = self.config.get_credentials(self.mode)
        
        self.base_url = self.credentials.get('base_url')
        self.app_key = self.credentials.get('app_key')
        self.app_secret = self.credentials.get('app_secret')
        self.account_number = self.credentials.get('account_number')
        self.account_product_code = self.credentials.get('account_product_code')
        
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        self.timeout = self.config.get('api.request_timeout', 10)
        self.max_retries = self.config.get('api.max_retries', 3)
        self.retry_delay = self.config.get('api.retry_delay', 1)
        
        logger.info(f"KIS API Client initialized in {self.mode} mode")
    
    def _get_headers(self, tr_id: str, include_token: bool = True) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": tr_id,
        }
        
        if include_token:
            if not self._access_token or self._is_token_expired():
                self._refresh_token()
            headers["authorization"] = f"Bearer {self._access_token}"
        
        return headers
    
    def _is_token_expired(self) -> bool:
        """토큰 만료 여부 확인"""
        if not self._token_expires_at:
            return True
        # 만료 5분 전에 갱신
        return datetime.now() >= (self._token_expires_at - timedelta(minutes=5))
    
    def _refresh_token(self):
        """OAuth2 토큰 발급/갱신"""
        logger.info("Refreshing access token...")
        
        url = f"{self.base_url}/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 86400)  # 기본 24시간
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info(f"Access token obtained, expires at {self._token_expires_at}")
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """API 요청 (재시도 로직 포함)"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts")
                    raise
    
    def get_stock_price(self, stock_code: str) -> StockQuote:
        """주식 현재가 조회
        
        Args:
            stock_code: 종목코드 (6자리)
        
        Returns:
            StockQuote 객체
        """
        tr_id = "FHKST01010100"  # 주식현재가 시세
        
        headers = self._get_headers(tr_id)
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        
        result = self._request(
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=headers,
            params=params
        )
        
        # 응답 데이터 파싱
        output = result.get('output', {})
        
        return StockQuote(
            stock_code=stock_code,
            stock_name=output.get('hts_kor_isnm', ''),
            current_price=int(output.get('stck_prpr', 0)),
            prev_close=int(output.get('stck_sdpr', 0)),
            open_price=int(output.get('stck_oprc', 0)),
            high_price=int(output.get('stck_hgpr', 0)),
            low_price=int(output.get('stck_lwpr', 0)),
            volume=int(output.get('acml_vol', 0))
        )
    
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """주문 실행
        
        Args:
            order: 주문 요청 객체
        
        Returns:
            OrderResponse 객체
        """
        # 매수/매도에 따른 TR_ID 설정
        if order.order_type.lower() == 'buy':
            tr_id = "TTTC0802U" if self.mode == 'real' else "VTTC0802U"
        else:  # sell
            tr_id = "TTTC0801U" if self.mode == 'real' else "VTTC0801U"
        
        headers = self._get_headers(tr_id)
        
        data = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "PDNO": order.stock_code,
            "ORD_DVSN": "01" if order.price > 0 else "01",  # 지정가/시장가
            "ORD_QTY": str(order.quantity),
            "ORD_UNPR": str(order.price) if order.price > 0 else "0"
        }
        
        logger.info(f"Placing order: {order.order_type} {order.stock_code} "
                   f"{order.quantity}주 @ {order.price}원")
        
        result = self._request(
            "POST",
            "/uapi/domestic-stock/v1/trading/order-cash",
            headers=headers,
            json=data
        )
        
        output = result.get('output', {})
        
        return OrderResponse(
            order_id=output.get('KRX_FWDG_ORD_ORGNO', '') + output.get('ODNO', ''),
            stock_code=order.stock_code,
            order_type=order.order_type,
            price=order.price,
            quantity=order.quantity,
            status="submitted",
            message=result.get('msg1', '')
        )
    
    def get_account_balance(self) -> AccountBalance:
        """계좌 잔고 조회"""
        tr_id = "TTTC8434R" if self.mode == 'real' else "VTTC8434R"
        
        headers = self._get_headers(tr_id)
        params = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        result = self._request(
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            headers=headers,
            params=params
        )
        
        output2 = result.get('output2', [{}])[0]
        
        total_asset = int(output2.get('tot_evlu_amt', 0))
        cash = int(output2.get('nxdy_excc_amt', 0))
        stock_value = int(output2.get('scts_evlu_amt', 0))
        profit_loss = int(output2.get('evlu_pfls_smtl_amt', 0))
        profit_loss_rate = float(output2.get('evlu_pfls_rt', 0))
        
        return AccountBalance(
            total_asset=total_asset,
            cash=cash,
            stock_value=stock_value,
            profit_loss=profit_loss,
            profit_loss_rate=profit_loss_rate
        )
    
    def get_positions(self) -> List[Position]:
        """보유 종목 조회"""
        tr_id = "TTTC8434R" if self.mode == 'real' else "VTTC8434R"
        
        headers = self._get_headers(tr_id)
        params = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        result = self._request(
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            headers=headers,
            params=params
        )
        
        positions = []
        for item in result.get('output1', []):
            if int(item.get('hldg_qty', 0)) > 0:
                positions.append(Position(
                    stock_code=item.get('pdno', ''),
                    stock_name=item.get('prdt_name', ''),
                    quantity=int(item.get('hldg_qty', 0)),
                    avg_price=int(float(item.get('pchs_avg_pric', 0))),
                    current_price=int(item.get('prpr', 0))
                ))
        
        return positions
