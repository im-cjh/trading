"""로깅 설정"""
import logging
import logging.config
import yaml
from pathlib import Path


def setup_logging(config_file: str = "config/logging_config.yaml"):
    """로깅 설정 초기화"""
    config_path = Path(config_file)
    
    # logs 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # 기본 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/trading_system.log', encoding='utf-8')
            ]
        )


def get_logger(name: str) -> logging.Logger:
    """로거 가져오기"""
    return logging.getLogger(name)
