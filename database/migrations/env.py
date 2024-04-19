# database/migrations/env.py

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace this with your actual database URL
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/db_name'

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

Base = declarative_base()

context.configure(
    engine=engine,
    target_metadata=Base.metadata,
    process_revision_directives=True,
    compare_type=True,
)
