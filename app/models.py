from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class PageContent(Base):
    __tablename__ = "page_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_name = Column(String(100), unique=True, nullable=False)
    title = Column(String(500))
    content = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    is_free = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    file_url = Column(String(500))
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    image_url = Column(String(500))
    link_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Добавляем недостающие модели
class Vacancy(Base):
    __tablename__ = "vacancies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    conditions = Column(Text)
    salary = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    value = Column(String(200), nullable=False)
    description = Column(String(200))
    order_index = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class Appeal(Base):
    __tablename__ = "appeals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_name = Column(String(100))
    user_contact = Column(String(100))
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)