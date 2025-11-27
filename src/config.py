"""설정 로더"""
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    """설정 관리 클래스"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._credentials: Dict[str, Any] = {}
        self._load_config()
        self._load_credentials()
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """YAML 파일 로드"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}")
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _load_config(self):
        """메인 설정 로드"""
        self._config = self._load_yaml("config.yaml")
        logger.info("Configuration loaded successfully")
    
    def _load_credentials(self):
        """인증 정보 로드"""
        self._credentials = self._load_yaml("credentials.yaml")
        if not self._credentials:
            logger.warning("Credentials not loaded. Using template values.")
            self._credentials = self._load_yaml("credentials.yaml.template")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 가져오기"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def get_credentials(self, mode: str = None) -> Dict[str, Any]:
        """API 인증 정보 가져오기
        
        Args:
            mode: 'mock' 또는 'real'. None이면 현재 모드 사용
        """
        if mode is None:
            mode = self.get_trading_mode()
        
        return self._credentials.get('kis_api', {}).get(mode, {})
    
    def get_trading_mode(self) -> str:
        """현재 거래 모드 가져오기"""
        # config.yaml의 trading_mode 우선, 없으면 credentials.yaml의 current_mode
        mode = self.get('trading_mode')
        if mode:
            return mode
        
        return self._credentials.get('current_mode', 'mock')
    
    def is_mock_mode(self) -> bool:
        """모의투자 모드 여부"""
        return self.get_trading_mode() == 'mock'
    
    def is_real_mode(self) -> bool:
        """실거래 모드 여부"""
        return self.get_trading_mode() == 'real'
    
    @property
    def trading_mode(self) -> str:
        """현재 거래 모드"""
        return self.get_trading_mode()


# 전역 설정 인스턴스
_config_instance = None


def get_config() -> Config:
    """설정 인스턴스 가져오기 (싱글톤)"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """설정 다시 로드"""
    global _config_instance
    _config_instance = Config()
    return _config_instance
