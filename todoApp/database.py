from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

postgreSQL_DATABASE_URL = "postgresql://harshshukla:8U3OJzWgCU98eFjDbiHgF6rLJWU3NjMo@dpg-cqj460aj1k6c739mdgug-a.oregon-postgres.render.com/todoapplicationdatabase_ehq2"

engine = create_engine(postgreSQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


