from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.database import engine
from app.models import User, Article, PageContent, Project, Document, Banner, Vacancy, Contact, Appeal

class BasicAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if username == "admin" and password == "admin":
            request.session.update({"token": "admin-token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == "admin-token"

# Модели админки
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.role, User.created_at]
    column_searchable_list = [User.username, User.email]
    form_excluded_columns = [User.id, User.created_at]

class ArticleAdmin(ModelView, model=Article):
    column_list = [Article.id, Article.title, Article.category, Article.published_at, Article.created_at]
    column_searchable_list = [Article.title]
    form_excluded_columns = [Article.id, Article.author_id, Article.created_at]

class PageContentAdmin(ModelView, model=PageContent):
    column_list = [PageContent.id, PageContent.page_name, PageContent.title, PageContent.is_active, PageContent.updated_at]
    column_searchable_list = [PageContent.page_name, PageContent.title]
    form_excluded_columns = [PageContent.id, PageContent.updated_at]

class ProjectAdmin(ModelView, model=Project):
    column_list = [Project.id, Project.title, Project.is_free, Project.is_active, Project.order_index]
    column_searchable_list = [Project.title]
    form_excluded_columns = [Project.id, Project.created_at]

class DocumentAdmin(ModelView, model=Document):
    column_list = [Document.id, Document.title, Document.category, Document.is_active, Document.created_at]
    column_searchable_list = [Document.title]
    form_excluded_columns = [Document.id, Document.created_at]

class BannerAdmin(ModelView, model=Banner):
    column_list = [Banner.id, Banner.title, Banner.is_active, Banner.order_index, Banner.created_at]
    column_searchable_list = [Banner.title]
    form_excluded_columns = [Banner.id, Banner.created_at]

class VacancyAdmin(ModelView, model=Vacancy):
    column_list = [Vacancy.id, Vacancy.title, Vacancy.is_active, Vacancy.created_at]
    column_searchable_list = [Vacancy.title]
    form_excluded_columns = [Vacancy.id, Vacancy.created_at]

class ContactAdmin(ModelView, model=Contact):
    column_list = [Contact.id, Contact.type, Contact.value, Contact.is_active, Contact.order_index]
    form_excluded_columns = [Contact.id]

class AppealAdmin(ModelView, model=Appeal):
    column_list = [Appeal.id, Appeal.type, Appeal.status, Appeal.created_at]
    form_excluded_columns = [Appeal.id, Appeal.created_at]

# Функция для инициализации админки
def init_admin(app):
    # Создаем экземпляр бэкенда аутентификации
    authentication_backend = BasicAuthBackend(secret_key="codd-admin-secret-2024")
    
    # Создаем экземпляр админки
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="ЦОДД Админка",
        logo_url=None,
    )
    
    # Регистрируем модели
    admin.add_view(UserAdmin)
    admin.add_view(ArticleAdmin)
    admin.add_view(PageContentAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(DocumentAdmin)
    admin.add_view(BannerAdmin)
    admin.add_view(VacancyAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(AppealAdmin)
    
    return admin