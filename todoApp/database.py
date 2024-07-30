from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#loaclDB=postgresql://harshshukla:test1234!@localhost:5433/TodoApplicationDatabase
#renderDB="postgresql://harshshukla:8U3OJzWgCU98eFjDbiHgF6rLJWU3NjMo@dpg-cqj460aj1k6c739mdgug-a.oregon-postgres.render.com/todoapplicationdatabase_ehq2"


prod_DB = "postgresql://harshshukla:8U3OJzWgCU98eFjDbiHgF6rLJWU3NjMo@dpg-cqj460aj1k6c739mdgug-a.oregon-postgres.render.com/todoapplicationdatabase_ehq2"

test_DB = "sqlite:///./todosapp.db"

engine = create_engine(prod_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


