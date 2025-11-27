"""한국투자증권 WebSocket 클라이언트"""
import asyncio
import websockets
import json
import aes128
from typing import Optional, Callable, Dict, Any
from ..config import get_config
from ..logger import get_logger
from .kis_models import WebSocketMessage

logger = get_logger(__name__)


class KISWebSocketClient:
    """한국투자증권 WebSocket 실시간 시세 클라이언트"""
    
    def __init__(self, mode: Optional[str] = None):
        """
        Args:
            mode: 'mock' 또는 'real'. None이면 설정 파일에서 읽음
        """
        self.config = get_config()
        self.mode = mode or self.config.get_trading_mode()
        self.credentials = self.config.get_credentials(self.mode)
        
        # WebSocket URL
        if self.mode == 'mock':
            self.ws_url = "ws://ops.koreainvestment.com:31000"
        else:
            self.ws_url = "ws://ops.koreainvestment.com:21000"
        
        self.app_key = self.credentials.get('app_key')
        self.app_secret = self.credentials.get('app_secret')
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.subscribed_stocks = set()
        
        # 메시지 핸들러
        self.message_handler: Optional[Callable[[WebSocketMessage], None]] = None
        
        logger.info(f"KIS WebSocket Client initialized in {self.mode} mode")
    
    async def connect(self):
        """WebSocket 연결"""
        try:
            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10
            )
            self.running = True
            logger.info(f"WebSocket connected to {self.ws_url}")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise
    
    async def disconnect(self):
        """WebSocket 연결 해제"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket disconnected")
    
    def _create_subscribe_message(self, stock_code: str, tr_type: str = "1") -> str:
        """실시간 시세 구독 메시지 생성
        
        Args:
            stock_code: 종목코드
            tr_type: 거래 유형 (1: 체결, 2: 호가)
        """
        header = {
            "approval_key": self.app_key,
            "custtype": "P",
            "tr_type": tr_type,
            "content-type": "utf-8"
        }
        
        body = {
            "input": {
                "tr_id": "H0STCNT0",  # 실시간 체결
                "tr_key": stock_code
            }
        }
        
        message = {
            "header": header,
            "body": body
        }
        
        return json.dumps(message)
    
    async def subscribe(self, stock_code: str):
        """종목 실시간 시세 구독
        
        Args:
            stock_code: 종목코드 (6자리)
        """
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        message = self._create_subscribe_message(stock_code)
        await self.websocket.send(message)
        self.subscribed_stocks.add(stock_code)
        
        logger.info(f"Subscribed to {stock_code}")
    
    async def unsubscribe(self, stock_code: str):
        """종목 실시간 시세 구독 해제
        
        Args:
            stock_code: 종목코드
        """
        if not self.websocket:
            return
        
        # 구독 해제 메시지 (tr_type을 2로 설정)
        message = self._create_subscribe_message(stock_code, tr_type="2")
        await self.websocket.send(message)
        self.subscribed_stocks.discard(stock_code)
        
        logger.info(f"Unsubscribed from {stock_code}")
    
    def _parse_message(self, raw_data: str) -> Optional[WebSocketMessage]:
        """WebSocket 메시지 파싱
        
        Args:
            raw_data: 원본 메시지
        
        Returns:
            WebSocketMessage 객체 또는 None
        """
        try:
            # 메시지 포맷: 헤더 | 본문
            parts = raw_data.split('|')
            
            if len(parts) < 3:
                return None
            
            # 헤더 파싱
            tr_id = parts[1]
            
            # 본문 파싱 (구분자로 분리된 데이터)
            data_parts = parts[3].split('^') if len(parts) > 3 else []
            
            # 체결 데이터 파싱 예시
            if tr_id == "H0STCNT0" and len(data_parts) >= 15:
                data = {
                    'stock_code': data_parts[0],
                    'current_price': int(data_parts[2]),
                    'change': int(data_parts[3]),
                    'change_rate': float(data_parts[4]),
                    'volume': int(data_parts[9]),
                    'timestamp': data_parts[1]
                }
                
                return WebSocketMessage(
                    message_type='tick',
                    stock_code=data['stock_code'],
                    data=data
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return None
    
    async def listen(self):
        """메시지 수신 루프"""
        if not self.websocket:
            raise RuntimeError("WebSocket not connected")
        
        logger.info("Started listening for messages")
        
        try:
            async for message in self.websocket:
                if not self.running:
                    break
                
                # 메시지 파싱
                parsed = self._parse_message(message)
                
                if parsed and self.message_handler:
                    try:
                        self.message_handler(parsed)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            if self.running:
                # 자동 재연결
                await self._reconnect()
        
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
    
    async def _reconnect(self):
        """자동 재연결"""
        logger.info("Attempting to reconnect...")
        
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                await self.connect()
                
                # 이전에 구독한 종목 재구독
                for stock_code in list(self.subscribed_stocks):
                    await self.subscribe(stock_code)
                
                logger.info("Reconnection successful")
                return
            
            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(retry_delay * (attempt + 1))
        
        logger.error("Failed to reconnect after maximum retries")
        self.running = False
    
    def set_message_handler(self, handler: Callable[[WebSocketMessage], None]):
        """메시지 핸들러 설정
        
        Args:
            handler: 메시지를 처리할 콜백 함수
        """
        self.message_handler = handler
    
    async def run(self, stock_codes: list):
        """WebSocket 실행 (연결, 구독, 수신)
        
        Args:
            stock_codes: 구독할 종목 코드 리스트
        """
        await self.connect()
        
        # 종목 구독
        for stock_code in stock_codes:
            await self.subscribe(stock_code)
        
        # 메시지 수신
        await self.listen()
