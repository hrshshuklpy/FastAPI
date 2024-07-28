from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

postgreSQL_DATABASE_URL = "postgresql://harshshukla:test1234!@localhost:5433/TodoApplicationDatabase"

engine = create_engine(postgreSQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


