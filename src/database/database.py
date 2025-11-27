"""데이터베이스 연결 및 세션 관리"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from pathlib import Path

from .models import Base
from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


class Database:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        self._initialize()
    
    def _initialize(self):
        """데이터베이스 초기화"""
        db_type = self.config.get('database.use', 'sqlite')
        
        if db_type == 'sqlite':
            # SQLite
            db_path = self.config.get('database.sqlite.path', 'data/trading.db')
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            db_url = f"sqlite:///{db_path}"
            logger.info(f"Using SQLite database: {db_path}")
        
        else:
            # PostgreSQL
            host = self.config.get('database.postgresql.host', 'localhost')
            port = self.config.get('database.postgresql.port', 5432)
            database = self.config.get('database.postgresql.database', 'trading_db')
            user = self.config.get('database.postgresql.user', 'trading_user')
            password = self.config.get('database.postgresql.password', 'trading_password')
            
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            logger.info(f"Using PostgreSQL database: {host}:{port}/{database}")
        
        self.engine = create_engine(
            db_url,
            echo=False,  # SQL 로깅
            pool_pre_ping=True  # 연결 상태 확인
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """테이블 생성"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """테이블 삭제 (주의!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """데이터베이스 세션 가져오기 (컨텍스트 매니저)"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 전역 데이터베이스 인스턴스
_db_instance = None


def get_database() -> Database:
    """데이터베이스 인스턴스 가져오기 (싱글톤)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션 가져오기"""
    db = get_database()
    return db.get_session()
