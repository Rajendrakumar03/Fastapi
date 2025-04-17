from sqlalchemy import Column,Integer,String,ForeignKey
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"

    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False)
    password= Column(String,nullable=False)
    email = Column(String,nullable=False)
    contact_number = Column(String)

    train_ticket = relationship("Ticket",back_populates="user")

class Ticket(Base):

    __tablename__ = "ticket"
    __table_args__= {
        'mysql_engine':'InnoDB'
    }

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    section = Column(String)
    seat = Column(Integer)
    price = Column(Integer)
    origin = Column(String)
    destination = Column(String)

    user = relationship(User,back_populates="train_ticket")