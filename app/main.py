from fastapi import FastAPI,Depends,Response,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# from .database import engine
from models import User,Ticket
from secure import hash_password,verify_password
from pydantic import BaseModel
# import models
import database
from fastapi.responses import JSONResponse

from auth import create_access_token,verify_token
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# Allow requests from the React frontend
origins = [
    "http://localhost:3000",  # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only frontend requests
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# models.Base.metadata.create_all(bind=engine)

def get_current_user(token:str=Depends(oauth2_scheme),db:Session= Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate", headers={"WWW-Authenticate": "Bearer"})
    user_id = verify_token(token,credentials_exception)
    user = db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise credentials_exception
    return user

class UserCreate(BaseModel):
    username : str
    password : str
    email : str
    contact_number : str

@app.post("/register/")
def register(user:UserCreate, db:Session= Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return JSONResponse (status_code=400,content={"message":"User already exist"}) 
    
    hashed_password = hash_password(user.password)

    new_user = User(
        username = user.username,
        password  = hashed_password,
        email = user.email,
        contact_number = user.contact_number
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse (status_code=200,content={"message":"Successfully registered"}) 

class UserLogin(BaseModel):
    email : str
    password : str

@app.post("/login/")
def login(user:UserLogin,db:Session=Depends(get_db)):

    db_user = db.query(User).filter(User.email==user.email).first()
    if not db_user:
        return JSONResponse (status_code=404,content= {"message":"User not found"})
    
    if not verify_password(user.password,db_user.password):
        return JSONResponse ( status_code=400,content={"message":"Invalid email or password"})
    
    token = create_access_token(data={"user_id":db_user.id})
    
    return JSONResponse(status_code=200,content= {"message":"Login Successful","user_id":db_user.id,"access_token":token,"token_type":"bearer"})

class PurchaseTicket(BaseModel):
    user_id : int
    section : str
    seat : int
    price : int
    origin : str
    destination : str

@app.post("/purchase/")
def purchase(ticket:PurchaseTicket,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    check_seat = db.query(Ticket).filter(Ticket.seat == ticket.seat,Ticket.section==ticket.section).first()
    if check_seat:
        return {"message":"Seat is already booked."}
    

    new_ticket = Ticket(
        user_id = ticket.user_id,
        section = ticket.section,
        seat = ticket.seat,
        price = ticket.price,
        origin = ticket.origin,
        destination = ticket.destination
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return {"message":"Ticket Purchased successfully"}

@app.get("/list_ticket/")
def ticket_list(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    ticket_list = db.query(Ticket).join(Ticket.user).all()
    if ticket_list:
        ticket_list = [
            {
                "username" : ticket.user.username,
                "seat" : ticket.seat,
                "section" : ticket.section,
                "origin":ticket.origin,
                "destination" : ticket.destination,
                "price" :ticket.price

            }
            for ticket in ticket_list
        ]
        # return {"tickets":ticket_list}
        return JSONResponse (status_code=200,content={"tickets":ticket_list}) 

    
    return JSONResponse(status_code=404,content={"message":"No ticket found"})


@app.get("/user_ticket/{id}")
def user_ticket(id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    
    
    ticket = db.query(Ticket).filter(Ticket.user_id==id).all()

    if ticket:
        user_ticket = [{
            "username" : tickets.user.username,
            "seat" : tickets.seat,
            "section" : tickets.section,
            "origin":tickets.origin,
            "destination" : tickets.destination,
            "price" :tickets.price
        }
        for tickets in ticket
        ]

        return JSONResponse (status_code=200,content={"tickets":user_ticket}) 

    
    return JSONResponse(status_code=404,content={"message":"No ticket found"})

