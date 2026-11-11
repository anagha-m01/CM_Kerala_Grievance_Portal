from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings

settings = get_settings()
kwargs = {'connect_args': {'check_same_thread': False}} if settings.database_uri.startswith('sqlite') else {'pool_pre_ping': True}
engine = create_engine(settings.database_uri, **kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
