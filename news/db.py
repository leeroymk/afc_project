from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from db_settings import URL_DB

# engine = create_engine('postgresql://LOGIN:PASSWORD@balarama.db.elephantsql.com:5432/DB_NAME')
engine = create_engine(URL_DB)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
