from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

engine = create_async_engine(
    settings.database_url,
    connent_args={"check_same_thread": False}
)
SessionLocal = async_sessionmaker( 
                                   class_=AsyncSession, 
                                   autocommit=False, 
                                   autoflush=False, 
                                   bind=engine
                )
Base = declarative_base() 

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

def init_db():
    Base.metadata.create_all(bind=engine)


