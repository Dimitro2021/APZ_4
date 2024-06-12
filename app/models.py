from sqlalchemy import Boolean, Column, Integer, Numeric, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    date = Column(Date)
    time = Column(Time)
    venue = Column(String(70))
    n_of_sits = Column(Integer)
    standard_ticket_price = Column(Numeric(10, 2))
    vip_ticket_price = Column(Numeric(10, 2))
    num_vip_tickets = Column(Integer, default=0)
    ticket = relationship("Ticket", back_populates="event")


class Performer(Base):
    __tablename__ = 'performer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    surname = Column(String(50))

class Ticket(Base):
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Integer)
    type = Column(String(50))
    status = Column(String(50))
    ticket_n = Column(Integer)
    user_id = Column(Integer)
    event_id = Column(Integer, ForeignKey('event.id'))
    event = relationship("Event", back_populates="ticket")

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    surname = Column(String(50))

class Contract(Base):
    __tablename__ = 'contract'

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    performer_id = Column(Integer, ForeignKey('performer.id'))
    event = relationship("Event")
    performer = relationship("Performer")