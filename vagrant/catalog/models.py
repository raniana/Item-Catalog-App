from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


    

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    picture = Column(String(250))
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    
    @property
    def serialize(self):
        return {
               'id'         :self.id,
               'name'       : self.name,
               }

    
class Item(Base):
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    brand = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    #category_name = Column(String(250), ForeignKey('category.name'))
    category = relationship(Category)
    user = relationship(User)


    
    @property
    def serialize(self):
        return{
            'name': self.name,
            'description': self.description,
            'brand': self.brand,
            'price': self.price,
            }


engine = create_engine('sqlite:///neighborhoodmarketplace.db')
Base.metadata.create_all(engine)
    
    
