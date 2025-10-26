from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class ArticleBase(BaseModel):
    title: str
    content: str
    category: str

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: UUID
    author_id: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)

class AppealBase(BaseModel):
    user_name: Optional[str] = None
    user_contact: Optional[str] = None
    type: str
    description: str

class AppealCreate(AppealBase):
    pass

class Appeal(AppealBase):
    id: UUID
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)