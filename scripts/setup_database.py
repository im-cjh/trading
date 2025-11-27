"""데이터베이스 초기화 스크립트"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger import setup_logging, get_logger
from src.database import get_database

setup_logging()
logger = get_logger(__name__)


def main():
    """데이터베이스 초기화"""
    logger.info("Initializing database...")
    
    db = get_database()
    
    # 테이블 생성
    db.create_tables()
    
    logger.info("Database initialized successfully!")
    logger.info("Tables created:")
    logger.info("  - trades")
    logger.info("  - position_history")
    logger.info("  - predictions")
    logger.info("  - account_snapshots")
    logger.info("  - strategy_versions")
    logger.info("  - market_data")


if __name__ == "__main__":
    main()
