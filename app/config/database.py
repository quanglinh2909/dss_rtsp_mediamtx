from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import importlib
import pkgutil
from contextlib import contextmanager

from app.model.base_model import BaseModel
from app import model as model_package  # import package app/model


class DatabaseManagerSqlite:
    def __init__(self):
        db_path =  'smart-signal.db'
        # Tạo thư mục data nếu chưa có
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Tạo engine với SQLite - cấu hình tối ưu cho concurrency
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections sau 1 giờ
            pool_size=30,       # Số connection trong pool
            max_overflow=60,    # Số connection tối đa có thể tạo thêm
            connect_args={
                'check_same_thread': False,
                'timeout': 30  # Timeout cho SQLite
            }
        )

        # Tạo scoped session factory - thread-safe
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)


    def create_tables(self):
        """Tạo tất cả bảng trong database - tự động scan từ app/model"""
        # Import tất cả modules trong app/model để đăng ký models vào metadata
        for _, module_name, _ in pkgutil.iter_modules(model_package.__path__):
            if module_name != 'base_model':  # Bỏ qua base_model
                importlib.import_module(f"app.model.{module_name}")
        
        # Tạo tất cả bảng từ BaseModel metadata
        BaseModel.metadata.create_all(bind=self.engine, checkfirst=True)


    def get_session(self):
        """Lấy session mới cho mỗi request"""
        return self.Session()

    @contextmanager
    def get_db_session(self):
        """Context manager để quản lý session lifecycle"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close_session(self):
        """Đóng scoped session"""
        self.Session.remove()


database_manager_sqlite = DatabaseManagerSqlite()