from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///apex_db.sqlite3')
SessionClass = sessionmaker(engine)
session=SessionClass()

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    category_id = Column(String, primary_key=True)

class Recuitment(Base):
    __tablename__ = 'recuitment'
    channel_id = Column(String)
    guild_id = Column(String, primary_key=True)

def add_category(category_id):
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

def add_recuit(guild_id, channel_id):
    recuit = Recuitment(channel_id=channel_id, guild_id=guild_id)
    session.add(recuit)
    session.commit()

def get_recuit(guild_id):
    recuit = session.query(Recuitment).filter(Recuitment.guild_id == guild_id).one_or_none()
    return recuit

def change_recuit(guild_id, channel_id):
    recuit = session.query(Recuitment).filter(Recuitment.guild_id == guild_id).one_or_none()
    if recuit is None:
        return recuit
    recuit.channel_id = channel_id

if __name__ == '__main__':
    Base.metadata.create_all(engine)