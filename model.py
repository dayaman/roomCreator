from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///apex_db.sqlite3')
SessionClass = sessionmaker(engine)
session=SessionClass()

Base = declarative_base()

class Category(Base):
    __tablename__ = "category"
    category_id = Column(String, primary_key=True)

def add(guild_id, category_id):
    ctgr = Category(category_id=category_id)
    session.add(ctgr)
    session.commit()

def get_categories():
    ctgrs = session.query(Category).all()
    return ctgrs

def delete_category(category_id):
    ctgr = session.query(Category).filter(Category.category_id == category_id).one()
    session.delete(ctgr)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)