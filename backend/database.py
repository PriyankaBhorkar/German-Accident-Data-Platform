# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# DB_USER = "kshitijsmacbookpro"

# DATABASE_URL = f"postgresql://{DB_USER}@localhost:5432/dbw_project"

# engine = create_engine(DATABASE_URL)

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER", "kshitijsmacbookpro")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dbw_project")

# include the password segment only if one is provided
_auth = DB_USER if not DB_PASSWORD else f"{DB_USER}:{DB_PASSWORD}"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{_auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)