from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
import os
from sqlalchemy import create_engine
import random
import string
from hashing import hash_password
from pydantic import BaseModel
from hashing import hash_password
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from sqlalchemy.orm import Session

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def initialize_database():
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

# Dependency to get the database session
def get_database() -> Generator[Session, None, None]:
    # Provide a database session to use within the request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    admin_flag = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow())

class SecretKey(Base):
    __tablename__ = "secret_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_value = Column(String, unique=True, index=True)

    @classmethod
    def add_or_update_key(cls, key_value):
        session = SessionLocal()
        existing_key = session.query(cls).first()
        if existing_key:
            existing_key.key_value = key_value
            print("Secret key updated successfully.")
        else:
            new_key = cls(key_value=key_value)
            session.add(new_key)
            print("Secret key added successfully.")
        session.commit()
        session.close()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey('users.username'))  # Foreign key referencing User table
    role_name = Column(String)
    tts_enabled = Column(Integer)
    ttm_enabled = Column(Integer)
    vc_enabled = Column(Integer)
    subscription_start_time = Column(DateTime, default=datetime.utcnow())
    subscription_end_time = Column(DateTime)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    subscription_end_time = Column(DateTime)
    
    roles = relationship("Role", back_populates="user")

# Add back reference to Role
Role.user = relationship("User", back_populates="roles")


class Email_User(Base):
    __tablename__ = "email_users"

    id = Column(String, primary_key=True, index=True, default=lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=64)))
    created_at = Column(DateTime, default=datetime.utcnow)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    status = Column(String, default="Active")
    role = Column(String, default="user")  # Default role is "user"

    @classmethod
    def create_user(cls, db: Session, email: str, password: str):
        hashed_password = hash_password(password)
        user = cls(email=email, password=hashed_password)
        db.add(user)
        db.commit()
        return user

class React_User(Base):
    __tablename__ = "react_users"

    id = Column(String, primary_key=True, index=True, default=lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=64)))
    created_at = Column(DateTime, default=datetime.utcnow)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    picture = Column(String)
    email_verified = Column(Boolean)
    role = Column(String, default="user")  # Default role is "user"

class React_user_Token(BaseModel):
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class AdminInfo(BaseModel):
    id: int
    username: str

