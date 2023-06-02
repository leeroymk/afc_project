from sqlalchemy import Column, Integer, String
from .db import Base, engine


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    # TODO: change date type from str to datetime
    date = Column(String)
    news_title = Column(String)
    news_context = Column(String)
    news_source = Column(String)

    def __repr__(self):
        return f'<News: {self.news_title} from  {self.news_source}>'


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
