from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import sys

# Настройка кодировки
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"

from app.database import get_db, engine, Base
from app.models import Article, Banner, PageContent, Project, Document, Vacancy, Contact, Appeal
from app.admin import init_admin  # Импортируем функцию инициализации

# Создаем папки если не существуют
os.makedirs("dosc", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ЦОДД API",
    description="API для системы ЦОДД Смоленской области", 
    version="1.0.0"
)

# Монтируем статические файлы
app.mount("/dosc", StaticFiles(directory="dosc"), name="dosc")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализируем админку
init_admin(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Мидлварь для установки кодировки всех ответов
@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)
    if hasattr(response, 'headers') and 'content-type' in response.headers:
        if 'application/json' in response.headers['content-type'] and 'charset' not in response.headers['content-type']:
            response.headers['content-type'] = 'application/json; charset=utf-8'
    return response

@app.get("/")
def read_root():
    return {
        'message': 'ЦОДД API работает!', 
        'version': '1.0.0',
        'admin_url': '/admin'
    }

# Утилита для правильного форматирования ответов
def format_response(data):
    """Форматирует данные для корректного отображения кириллицы"""
    if isinstance(data, dict):
        return {key: format_response(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_response(item) for item in data]
    elif isinstance(data, str):
        return data
    else:
        return data

# 1. ГЛАВНАЯ СТРАНИЦА
@app.get("/api/main-page")
def get_main_page(db: Session = Depends(get_db)):
    """Данные для главной страницы"""
    articles = db.query(Article).filter(Article.published_at != None).order_by(Article.published_at.desc()).limit(3).all()
    banners = db.query(Banner).filter(Banner.is_active == True).order_by(Banner.order_index).all()
    
    main_content = db.query(PageContent).filter(
        PageContent.page_name == "main", 
        PageContent.is_active == True
    ).first()
    
    response_data = {
        "content": {
            "title": main_content.title if main_content else "ЦОДД Смоленской области",
            "text": main_content.content if main_content else "Центр общественного доступа к данным Смоленской области",
            "image_url": main_content.image_url if main_content else None
        },
        "latest_news": [
            {
                "id": str(article.id),
                "title": article.title if article.title else "Заголовок новости",
                "preview": article.content[:100] + "..." if article.content and len(article.content) > 100 else article.content or "Описание новости",
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
            for article in articles
        ],
        "banners": [
            {
                "id": str(banner.id), 
                "title": banner.title if banner.title else "Баннер",
                "image_url": banner.image_url,
                "link_url": banner.link_url
            }
            for banner in banners
        ]
    }
    
    return format_response(response_data)

# 2. НОВОСТИ
@app.get("/api/news")
def get_news_list(
    page: int = 1, 
    limit: int = 10, 
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Список новостей с пагинацией"""
    offset = (page - 1) * limit
    query = db.query(Article).filter(Article.published_at != None)
    
    if category:
        query = query.filter(Article.category == category)
    
    total = query.count()
    articles = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()
    
    response_data = {
        "articles": [
            {
                "id": str(article.id),
                "title": article.title or "Без заголовка",
                "preview": article.content[:200] + "..." if article.content and len(article.content) > 200 else article.content or "Содержание новости",
                "category": article.category or "general",
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
            for article in articles
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if limit > 0 else 0
        }
    }
    
    return format_response(response_data)

@app.get("/api/news/{article_id}")
def get_news_detail(article_id: str, db: Session = Depends(get_db)):
    """Детальная страница новости"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
    except:
        raise HTTPException(status_code=400, detail="Неверный ID новости")
    
    if not article:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    response_data = {
        "id": str(article.id),
        "title": article.title or "Без заголовка",
        "content": article.content or "Содержание новости",
        "category": article.category or "general",
        "published_at": article.published_at.isoformat() if article.published_at else None
    }
    
    return format_response(response_data)

# 3. ВАКАНСИИ
@app.get("/api/vacancies")
def get_vacancies(db: Session = Depends(get_db)):
    """Список активных вакансий"""
    vacancies = db.query(Vacancy).filter(Vacancy.is_active == True).order_by(Vacancy.created_at.desc()).all()
    
    response_data = {
        "vacancies": [
            {
                "id": str(vacancy.id),
                "title": vacancy.title or "Новая вакансия",
                "description": vacancy.description or "Описание вакансии",
                "requirements": vacancy.requirements or "Требования к кандидату",
                "conditions": vacancy.conditions or "Условия работы",
                "salary": vacancy.salary or "По договоренности",
                "created_at": vacancy.created_at.isoformat() if vacancy.created_at else None
            }
            for vacancy in vacancies
        ]
    }
    
    return format_response(response_data)

# 4. КОНТАКТЫ
@app.get("/api/contacts")
def get_contacts(db: Session = Depends(get_db)):
    """Контактная информация"""
    contacts = db.query(Contact).filter(Contact.is_active == True).order_by(Contact.order_index).all()
    
    if not contacts:
        contacts_data = [
            {
                "type": "phone",
                "value": "+7 (4812) 12-34-56",
                "description": "Основной телефон"
            },
            {
                "type": "email", 
                "value": "codd@smolensk.ru",
                "description": "Электронная почта"
            },
            {
                "type": "address",
                "value": "г. Смоленск, ул. Примерная, д. 1",
                "description": "Адрес офиса"
            }
        ]
    else:
        contacts_data = [
            {
                "id": str(contact.id),
                "type": contact.type or "contact",
                "value": contact.value or "Не указано",
                "description": contact.description or "Контактная информация"
            }
            for contact in contacts
        ]
    
    response_data = {"contacts": contacts_data}
    return format_response(response_data)

# 5. УСЛУГИ
@app.get("/api/services")
def get_services(db: Session = Depends(get_db)):
    """Данные для страницы услуг"""
    services_content = db.query(PageContent).filter(
        PageContent.page_name == "services", 
        PageContent.is_active == True
    ).first()
    
    projects = db.query(Project).filter(
        Project.is_active == True
    ).order_by(Project.order_index).all()
    
    response_data = {
        "content": {
            "title": services_content.title if services_content else "Услуги ЦОДД",
            "text": services_content.content if services_content else "Мы предоставляем широкий спектр услуг для граждан и организаций",
            "image_url": services_content.image_url if services_content else None
        },
        "projects": [
            {
                "id": str(project.id),
                "title": project.title or "Проект",
                "description": project.description or "Описание проекта",
                "image_url": project.image_url,
                "is_free": project.is_free if project.is_free is not None else True
            }
            for project in projects
        ]
    }
    
    return format_response(response_data)

# 6. О ЦОДД
@app.get("/api/about")
def get_about_page(db: Session = Depends(get_db)):
    """Данные для страницы 'О ЦОДД'"""
    about_content = db.query(PageContent).filter(
        PageContent.page_name == "about", 
        PageContent.is_active == True
    ).first()
    
    response_data = {
        "content": {
            "title": about_content.title if about_content else "О ЦОДД Смоленской области",
            "text": about_content.content if about_content else "Центр общественного доступа к данным - это современная платформа для взаимодействия граждан и власти",
            "image_url": about_content.image_url if about_content else None
        }
    }
    
    return format_response(response_data)

# 7. ДОКУМЕНТЫ
@app.get("/api/documents")
def get_documents(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Список документов"""
    query = db.query(Document).filter(Document.is_active == True)
    
    if category:
        query = query.filter(Document.category == category)
    
    documents = query.order_by(Document.created_at.desc()).all()
    
    response_data = {
        "documents": [
            {
                "id": str(doc.id),
                "title": doc.title or "Документ",
                "file_url": doc.file_url,
                "category": doc.category or "general",
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in documents
        ]
    }
    
    return format_response(response_data)

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("other"),
    db: Session = Depends(get_db)
):
    """Загрузка документа"""
    # Проверяем тип файла
    allowed_extensions = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'}
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")
    
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"dosc/{filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    
    document = Document(
        title=title,
        file_url=f"/dosc/{filename}",
        category=category
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    response_data = {
        "message": "Документ успешно загружен", 
        "document": {
            "id": str(document.id),
            "title": document.title,
            "file_url": document.file_url,
            "category": document.category
        }
    }
    
    return format_response(response_data)

# 8. ОБРАТНАЯ СВЯЗЬ
@app.post("/api/appeals")
def create_appeal(
    user_name: Optional[str] = Form(None),
    user_contact: str = Form(...),
    appeal_type: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    """Создание обращения"""
    appeal = Appeal(
        user_name=user_name,
        user_contact=user_contact,
        type=appeal_type,
        description=description
    )
    
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    
    response_data = {
        "message": "Обращение успешно создано", 
        "id": str(appeal.id)
    }
    
    return format_response(response_data)

@app.get("/api/banners")
def get_banners(db: Session = Depends(get_db)):
    """Получить все активные баннеры"""
    banners = db.query(Banner).filter(Banner.is_active == True).order_by(Banner.order_index).all()
    
    response_data = {
        "banners": [
            {
                "id": str(banner.id),
                "title": banner.title or "Баннер",
                "image_url": banner.image_url,
                "link_url": banner.link_url
            }
            for banner in banners
        ]
    }
    
    return format_response(response_data)

@app.get("/api/projects")
def get_projects(is_free: Optional[bool] = None, db: Session = Depends(get_db)):
    """Получить проекты (с фильтром по бесплатности)"""
    query = db.query(Project).filter(Project.is_active == True)
    
    if is_free is not None:
        query = query.filter(Project.is_free == is_free)
    
    projects = query.order_by(Project.order_index).all()
    
    response_data = {
        "projects": [
            {
                "id": str(project.id),
                "title": project.title or "Проект",
                "description": project.description or "Описание проекта",
                "image_url": project.image_url,
                "is_free": project.is_free
            }
            for project in projects
        ]
    }
    
    return format_response(response_data)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "API работает корректно",
        "timestamp": datetime.now().isoformat()
    }