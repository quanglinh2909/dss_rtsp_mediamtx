from abc import ABC
from typing import List, Optional, TypeVar, Generic, Type, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from app.config.database import database_manager_sqlite
from app.model.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseService(Generic[T], ABC):
    """
    Base service class để cung cấp các CRUD operations cơ bản
    """

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self._db_manager = database_manager_sqlite

    @contextmanager
    def get_session(self):
        """Context manager để quản lý session cho mỗi operation"""
        session = self._db_manager.get_session()
        try:
            yield session
        finally:
            session.close()

    def create(self, **kwargs) -> Optional[T]:
        """
        Tạo một record mới
        Args:
            **kwargs: Các field của model
        Returns:
            Instance của model đã tạo hoặc None nếu có lỗi
        """
        with self.get_session() as session:
            try:
                instance = self.model_class(**kwargs)
                session.add(instance)
                session.commit()
                session.refresh(instance)  # Refresh để lấy ID mới
                return instance
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error creating {self.model_class.__name__}", e)
                return None

    def get_by_id(self, record_id: str) -> Optional[T]:
        """
        Lấy record theo ID
        Args:
            record_id: ID của record
        Returns:
            Instance của model hoặc None nếu không tìm thấy
        """
        with self.get_session() as session:
            try:
                return session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
            except SQLAlchemyError as e:
                self._handle_error(f"Error getting {self.model_class.__name__} by id", e)
                return None

    def get_all(self, limit: Optional[int] = None, offset: int = 0,
                order_by: Optional[str] = None, order_desc: bool = False) -> List[T]:
        """
        Lấy tất cả records
        Args:
            limit: Giới hạn số lượng record
            offset: Bỏ qua số lượng record từ đầu
            order_by: Tên field để sắp xếp (ví dụ: 'created_at', 'name')
            order_desc: True = DESC, False = ASC (mặc định)
        Returns:
            List các instance của model
        """
        with self.get_session() as session:
            try:
                query = session.query(self.model_class)
                if order_by and hasattr(self.model_class, order_by):
                    col = getattr(self.model_class, order_by)
                    query = query.order_by(col.desc() if order_desc else col.asc())
                if offset > 0:
                    query = query.offset(offset)
                if limit:
                    query = query.limit(limit)
                return query.all()
            except SQLAlchemyError as e:
                self._handle_error(f"Error getting all {self.model_class.__name__}", e)
                return []

    def update(self, record_id: str, **kwargs) -> Optional[T]:
        """
        Cập nhật record theo ID
        Args:
            record_id: ID của record cần update
            **kwargs: Các field cần update
        Returns:
            Instance đã update hoặc None nếu có lỗi
        """
        with self.get_session() as session:
            try:
                instance = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if not instance:
                    return None

                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)

                session.commit()
                session.refresh(instance)
                return instance
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error updating {self.model_class.__name__}", e)
                return None

    def delete(self, record_id: str) -> bool:
        """
        Xóa record theo ID
        Args:
            record_id: ID của record cần xóa
        Returns:
            True nếu xóa thành công, False nếu có lỗi
        """
        with self.get_session() as session:
            try:
                instance = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if not instance:
                    return False

                session.delete(instance)
                session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error deleting {self.model_class.__name__}", e)
                return False

    def delete_many(self, record_ids: List[str]) -> int:
        """
        Xóa nhiều records cùng lúc
        Args:
            record_ids: List các ID cần xóa
        Returns:
            Số lượng records đã xóa thành công
        """
        with self.get_session() as session:
            deleted_count = 0
            try:
                for record_id in record_ids:
                    instance = session.query(self.model_class).filter(
                        self.model_class.id == record_id
                    ).first()
                    
                    if instance:
                        session.delete(instance)
                        deleted_count += 1
                
                session.commit()
                return deleted_count
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error deleting multiple {self.model_class.__name__}", e)
                return 0

    def delete_all(self) -> int:
        """
        Xóa tất cả records
        Returns:
            Số lượng records đã xóa thành công
        """
        with self.get_session() as session:
            try:
                deleted_count = session.query(self.model_class).delete()
                session.commit()
                return deleted_count
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error deleting all {self.model_class.__name__}", e)
                return 0

    def count(self) -> int:
        """
        Đếm tổng số records
        Returns:
            Số lượng records
        """
        with self.get_session() as session:
            try:
                return session.query(self.model_class).count()
            except SQLAlchemyError as e:
                self._handle_error(f"Error counting {self.model_class.__name__}", e)
                return 0

    def exists(self, record_id: str) -> bool:
        """
        Kiểm tra record có tồn tại không
        Args:
            record_id: ID cần kiểm tra
        Returns:
            True nếu tồn tại, False nếu không
        """
        with self.get_session() as session:
            try:
                return session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first() is not None
            except SQLAlchemyError as e:
                self._handle_error(f"Error checking existence of {self.model_class.__name__}", e)
                return False

    def find_by(self, **kwargs) -> List[T]:
        """
        Tìm records theo điều kiện
        Args:
            **kwargs: Các điều kiện tìm kiếm
        Returns:
            List các instance thỏa mãn điều kiện
        """
        with self.get_session() as session:
            try:
                query = session.query(self.model_class)
                for key, value in kwargs.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                return query.all()
            except SQLAlchemyError as e:
                self._handle_error(f"Error finding {self.model_class.__name__} by conditions", e)
                return []

    def find_one_by(self, **kwargs) -> Optional[T]:
        """
        Tìm một record theo điều kiện
        Args:
            **kwargs: Các điều kiện tìm kiếm
        Returns:
            Instance đầu tiên thỏa mãn điều kiện hoặc None
        """
        with self.get_session() as session:
            try:
                query = session.query(self.model_class)
                for key, value in kwargs.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                return query.first()
            except SQLAlchemyError as e:
                self._handle_error(f"Error finding one {self.model_class.__name__} by conditions", e)
                return None

    def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """
        Tạo nhiều records cùng lúc
        Args:
            items: List các dict chứa data cho từng record
        Returns:
            List các instance đã tạo
        """
        with self.get_session() as session:
            created_items = []
            try:
                for item_data in items:
                    instance = self.model_class(**item_data)
                    session.add(instance)
                    created_items.append(instance)

                session.commit()

                # Refresh tất cả instances để lấy ID
                for instance in created_items:
                    session.refresh(instance)

                return created_items
            except SQLAlchemyError as e:
                session.rollback()
                self._handle_error(f"Error bulk creating {self.model_class.__name__}", e)
                return []

    def get_paginated(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Lấy data theo trang
        Args:
            page: Số trang (bắt đầu từ 1)
            per_page: Số records mỗi trang
        Returns:
            Dict chứa data và thông tin phân trang
        """
        try:
            total = self.count()
            offset = (page - 1) * per_page
            items = self.get_all(limit=per_page, offset=offset)

            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        except Exception as e:
            self._handle_error(f"Error getting paginated {self.model_class.__name__}", e)
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            }

    def _handle_error(self, message: str, error: Exception):
        """
        Xử lý lỗi - có thể override trong class con
        Args:
            message: Thông báo lỗi
            error: Exception object
        """
        print(f"{message}: {str(error)}")
        # Có thể thêm logging ở đây

    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate dữ liệu trước khi create/update
        Args:
            data: Dữ liệu cần validate
        Returns:
            Dữ liệu đã được validate và clean
        Raises:
            ValueError: Nếu dữ liệu không hợp lệ
        """
        return data

    def create_validated(self, **kwargs) -> Optional[T]:
        """
        Tạo record với validation
        Args:
            **kwargs: Dữ liệu để tạo record
        Returns:
            Instance đã tạo hoặc None nếu có lỗi
        """
        try:
            validated_data = self.validate_data(kwargs)
            return self.create(**validated_data)
        except ValueError as e:
            self._handle_error(f"Validation error for {self.model_class.__name__}", e)
            return None

    def update_validated(self, record_id: str, **kwargs) -> Optional[T]:
        """
        Update record với validation
        Args:
            record_id: ID của record cần update
            **kwargs: Dữ liệu update
        Returns:
            Instance đã update hoặc None nếu có lỗi
        """
        try:
            validated_data = self.validate_data(kwargs)
            return self.update(record_id, **validated_data)
        except ValueError as e:
            self._handle_error(f"Validation error for {self.model_class.__name__}", e)
            return None