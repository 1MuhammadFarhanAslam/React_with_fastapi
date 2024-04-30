from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
import os
from sqlalchemy import create_engine
import random
import string
from sqlalchemy import ARRAY

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    email_status = Column(String)
    roles = Column(ARRAY(String))
    status = Column(String)
    password_reset_code = Column(String, default=None)
    reset_access_token = Column(String, default=None)
    verification_token = Column(String, default=None)

class Google_User(Base):
    __tablename__ = "google_users"

    id = Column(String, primary_key=True, index=True, default=lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=64)))
    created_at = Column(DateTime, default=datetime.utcnow)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    picture = Column(String)
    email_status = Column(Boolean)
    role = Column(String, default="user")  # Default role is "user"

class Google_user_Token(BaseModel):
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class AdminInfo(BaseModel):
    id: int
    username: str


class AccessToken(Base):
    __tablename__ = 'access_tokens'

    id = Column(Integer, primary_key=True)  # Define a primary key column
    email = Column(String, unique=True)
    JWT_Token = Column(String)


# Model for password reset request
class PasswordResetRequest(BaseModel):
    email: str

# Model for password reset submission
class PasswordResetSubmit(BaseModel):
    reset_code: str
    email: str
    new_password: str
    