from datetime import date, time
from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional


class Event(BaseModel):
    name: str
    venue: str
    n_of_sits: int  # Number of total seats
    date: date
    time: time
    standard_ticket_price: float  # Price for standard tickets
    vip_ticket_price: float       # Price for VIP tickets
    num_vip_tickets: int = 0      # Number of VIP tickets, defaults to 0 if not provided

class Event_w_id(Event):
    id: int

class Ticket(BaseModel):
    class TicketStatus(str, Enum):
        available = "available"
        sold = "sold"
        reserved = "reserved"

    class TicketType(str, Enum):
        standard = "standard"
        vip = "vip"

    price: int
    type: TicketType
    status: Optional[TicketStatus] = "available"  # Set initial status to "available"
    ticket_n: int
    event_id: int
    user_id: int

    @validator('status')
    def validate_status(cls, v):
        if v not in Ticket.TicketStatus.__members__:
            raise ValueError("Invalid status. Must be one of: sold, reserved, available")
        return v

    @validator('type')
    def validate_type(cls, v):
        if v not in Ticket.TicketType.__members__:
            raise ValueError("Invalid type. Must be one of: VIP, standard")
        return v

class Performer(BaseModel):
    name: str
    surname: str

class User(BaseModel):
    name: str
    surname: str

class User_w_id(User):
    id: int

class Contract(BaseModel):
    event_id: int
    performer_id: int
