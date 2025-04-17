from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta,declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://raji:raji%40123@localhost:5432/fast_api"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()