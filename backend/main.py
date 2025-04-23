from datetime import timedelta

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from crypt import CryptoHelper
from db import Core, StatementBuilder, QueryResultWrapper
from fastapi.responses import JSONResponse
import security
app = FastAPI()

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    two_fa: bool = False
    Address: str = None

class UserPublic(BaseModel):
    name: str
    email: EmailStr
    two_fa: bool = False
    Address: str = None

class TokenData(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic

@app.post("/register", response_model=User)
def register(user: User):
    user_data = user.dict()
    crypto_helper = CryptoHelper()
    core = Core()
    user_data["password"] = crypto_helper.hash_password(user_data["password"])
    StatementBuilder(core.users, core.connection).insert(user_data).execute()


@app.post("/login", response_model=UserPublic)
def login(user: User, request: Request):
    client_ip = request.client.host
    core = Core()
    crypto = CryptoHelper()
    db_result = StatementBuilder(core.users, core.connection).select(email=user.email).execute()
    user_row = QueryResultWrapper(db_result).first_dict()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    if not crypto.verify_password(user.password, user_row["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    token = security.create_access_token(data={"sub": user_row["email"]})
    StatementBuilder(core.users, core.connection).update(
        {"Adress": client_ip},
        email=user.email
    ).execute()
    return TokenData(
        access_token=token,
        token_type="bearer",
        user= UserPublic(
            name=user_row["name"],
            email=user_row["email"],
            two_fa=user_row["two_fa"],
            Address=client_ip,
        )
    )