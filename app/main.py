from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from typing import Annotated, List
from fastapi.params import Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import distinct, text
import uvicorn

import models
from database import engine, SessionLocal, Base
from bm_classes import *

app = FastAPI()
models.Base.metadata.create_all(bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# post
@app.post("/ticket/", status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: Ticket, db: db_dependency):
    event_exists = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()
    if not event_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()

@app.post("/event/", status_code=status.HTTP_201_CREATED)
def create_event(event: Event, db: db_dependency):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()

    create_tickets_for_event(db_event.id, db_event.n_of_sits, db_event.standard_ticket_price, 
                             db_event.vip_ticket_price, db_event.num_vip_tickets, db)
    return db_event

def create_tickets_for_event(event_id, total_seats, standard_price, vip_price, num_vip, db: Session):
    for seat in range(1, total_seats + 1):
        if seat <= num_vip:
            ticket_type = "VIP"
            price = vip_price
        else:
            ticket_type = "standard"
            price = standard_price
        ticket = models.Ticket(
            event_id=event_id,
            price=price,
            status="available",
            type=ticket_type,
        )
        db.add(ticket)
    db.commit()

@app.post("/performer/", status_code=status.HTTP_201_CREATED)
def create_performer(performer: Performer, db: db_dependency):
    db_performer = models.Performer(**performer.dict())
    db.add(db_performer)
    db.commit()

@app.post("/user/", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()


# update
@app.put("/ticket/{ticket_id}", status_code=status.HTTP_200_OK)
def update_ticket(ticket_id: int, ticket_update: Ticket, db: db_dependency):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    event_exists = db.query(models.Event).filter(models.Event.id == ticket_update.event_id).first()
    if not event_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event not found")

    # Check if user_id is 0 if status is "available" or if user_id exists if status is other than "available"
    if (ticket_update.status == Ticket.TicketStatus.available and ticket_update.user_id != 0) or \
       (ticket_update.status != Ticket.TicketStatus.available and not db.query(models.User).filter(models.User.id == ticket_update.user_id).first()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id for ticket status")

    for field, value in ticket_update.dict().items():
        setattr(db_ticket, field, value)
    db.commit()
    return db_ticket

@app.put("/event/{event_id}", status_code=status.HTTP_200_OK)
def update_event(event_id: int, event_update: Event, db: db_dependency):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in event_update.dict().items():
        setattr(db_event, field, value)
    db.commit()
    return db_event

@app.put("/performer/{performer_id}", status_code=status.HTTP_200_OK)
def update_performer(performer_id: int, performer_update: Performer, db: db_dependency):
    db_performer = db.query(models.Performer).filter(models.Performer.id == performer_id).first()
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    for field, value in performer_update.dict().items():
        setattr(db_performer, field, value)
    db.commit()
    return db_performer

@app.put("/user/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_update: User, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_update.dict().items():
        setattr(db_user, field, value)
    db.commit()
    return db_user


# delete
@app.delete("/ticket/{ticket_id}", status_code=status.HTTP_200_OK)
def delete_ticket(ticket_id: int, db : db_dependency):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail=f"Ticket with id {ticket_id} was not found")
    db.delete(db_ticket)
    db.commit()

@app.delete("/event/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(event_id: int, db: db_dependency):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event was not found")
    
    # Delete all tickets related to the event
    db.query(models.Ticket).filter(models.Ticket.event_id == event_id).delete()
    
    # Delete all performer-event relations from the contract table
    db.query(models.Contract).filter(models.Contract.event_id == event_id).delete()

    db.delete(db_event)
    db.commit()

@app.delete("/performer/{performer_id}", status_code=status.HTTP_200_OK)
def delete_performer(performer_id: int, db : db_dependency):
    db_performer = db.query(models.Performer).filter(models.Performer.id == performer_id).first()
    if db_performer is None:
        raise HTTPException(status_code=404, detail="Performer was not found")

    # Delete all performer-event relations from the contract table
    db.query(models.Contract).filter(models.Contract.performer_id == performer_id).delete()

    db.delete(db_performer)
    db.commit()

@app.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Change the status of tickets belonging to the deleted user to "available"
    db.query(models.Ticket).filter(models.Ticket.user_id == user_id).update({models.Ticket.status: "available"})

    db.delete(db_user)
    db.commit()


# get all events
def get_events_with_id(db: Session):
    events = db.query(models.Event).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    return [Event_w_id(**event.__dict__) for event in events]

@app.get("/events/", response_model=List[Event_w_id], status_code=status.HTTP_200_OK)
def read_events(db: Session = Depends(get_db)):
    return get_events_with_id(db)


# get
@app.get("/ticket/{ticket_id}", status_code=status.HTTP_200_OK)
def read_ticket(ticket_id: int, db: db_dependency):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db_ticket

@app.get("/event/{event_id}", status_code=status.HTTP_200_OK)
def read_event(event_id: int, db: db_dependency):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.get("/performer/{performer_id}", status_code=status.HTTP_200_OK)
def read_performer(performer_id: int, db: db_dependency):
    performer = db.query(models.Performer).filter(models.Performer.id == performer_id).first()
    if performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    return performer

@app.get("/events_available/")
def get_available_events(date: datetime = Query(None, description="Date to check available events (i.e. 2024-05-01)"), db: Session = Depends(get_db)):
    if date is None:
        raise HTTPException(status_code=400, detail="Please provide a valid date parameter")

    current_date = datetime.now()

    # Query events that occur before the provided date and after the current date
    events = db.query(models.Event).filter(models.Event.date < date, models.Event.date > current_date).all()
    if not events:
        return {"message": "No events found"}

    # For each event, count the number of available seats
    available_events = []
    for event in events:
        available_seats = db.query(models.Ticket).filter(
            models.Ticket.event_id == event.id,
            models.Ticket.status == "available"
        ).count()
        available_events.append({
            "event_id": event.id,
            "n_of_sits": event.n_of_sits,
            "n_of_available_sits": available_seats
        })

    return available_events


# ticket reservation
async def release_ticket(ticket_id: int, db: Session):
    await asyncio.sleep(900)  # 15 minutes delay (900 seconds)
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket and ticket.status == "reserved":
        ticket.status = "available"
        ticket.user_id = None
        print(f'ticket with id {ticket_id} is again "avaliable"')
        db.commit()

@app.put("/ticket/reserve/{ticket_id}/{user_id}")
def reserve_ticket(ticket_id: int, user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if ticket.status != "available":
        raise HTTPException(status_code=400, detail="Ticket is not available for reservation")

    ticket.status = "reserved"
    ticket.user_id = user_id
    db.commit()

    
    # Schedule the ticket release after 15 minutes
    expiration_time = datetime.now() + timedelta(minutes=1)
    background_tasks.add_task(release_ticket, ticket_id, db)
    
    return {"message": "Ticket reserved successfully", "expiration_time": expiration_time}


# user reserved event_id
@app.get("/event/{event_id}/reserved_users/", response_model=List[User_w_id])
def get_reserved_users(event_id: int, db: Session = Depends(get_db)):
    # Join the Ticket and User tables to retrieve users who reserved tickets for the event
    reserved_users = db.query(models.User).join(models.Ticket, models.Ticket.user_id == models.User.id).filter(models.Ticket.event_id == event_id).filter(models.Ticket.status == "reserved").all()

    if not reserved_users:
        raise HTTPException(status_code=404, detail="No users have reserved tickets for this event")

    return [User_w_id(**user.__dict__) for user in reserved_users]

# user that bought event_id
@app.get("/event/{event_id}/reserved_users/", response_model=List[User_w_id])
def get_bought_users(event_id: int, db: Session = Depends(get_db)):
    # Join the Ticket and User tables to retrieve users who bought tickets for the event
    bought_users = db.query(models.User).join(models.Ticket, models.Ticket.user_id == models.User.id).filter(models.Ticket.event_id == event_id).filter(models.Ticket.status == "sold").all()

    if not bought_users:
        raise HTTPException(status_code=404, detail="No users have reserved tickets for this event")

    return [User_w_id(**user.__dict__) for user in bought_users]


# contract performer to event
@app.post("/event/{event_id}/contract_performer/{performer_id}")
def contract_performer(event_id: int, performer_id: int, db: Session = Depends(get_db)):
    # Check if the event exists
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if the performer exists
    performer = db.query(models.Performer).filter(models.Performer.id == performer_id).first()
    if not performer:
        raise HTTPException(status_code=404, detail="Performer not found")

    # Check if the performer is already contracted for the event
    existing_contract = db.query(models.Contract).filter(models.Contract.event_id == event_id, models.Contract.performer_id == performer_id).first()
    if existing_contract:
        raise HTTPException(status_code=400, detail="Performer is already contracted for this event")

    # Create a new contract
    contract = models.Contract(event_id=event_id, performer_id=performer_id)
    db.add(contract)
    db.commit()

    return {"message": "Performer contracted successfully"}

# performers with contracts
@app.get("/performers/with_contracts/", response_model=List[Performer])
def get_performers_with_contracts(db: Session = Depends(get_db)):
    # Query distinct performers mentioned in contracts
    performers_with_contracts = db.query(models.Performer).join(models.Contract, models.Performer.id == models.Contract.performer_id).distinct(models.Performer.id).all()
    
    if not performers_with_contracts:
        raise HTTPException(status_code=404, detail="No performers with contracts found")
    
    return performers_with_contracts


# user's tickets
@app.get("/user/{user_id}/ickets/", response_model=List[Ticket], status_code=status.HTTP_200_OK)
def get_sold_tickets(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    sold_tickets = db.query(models.Ticket).filter(models.Ticket.user_id == user_id, models.Ticket.status == "sold").all()
    if not sold_tickets:
        raise HTTPException(status_code=404, detail="User has no sold tickets")
    
    return sold_tickets


@app.put("/user/{user_id}/buy-ticket/{ticket_id}/", status_code=status.HTTP_200_OK)
def buy_ticket(user_id: int, ticket_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.status == "sold" or (ticket.status == 'reserved' and ticket.user_id != user_id):
        raise HTTPException(status_code=400, detail="Ticket is not available")
    
    ticket.status = "sold"
    ticket.user_id = user_id
    db.commit()
    
    return {"message": "Ticket purchased successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
