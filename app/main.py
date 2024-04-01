from fastapi import FastAPI
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, user, login, react, react_1

app = FastAPI()


# Get the database URL from the environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
# Check if DATABASE_URL is defined
if DATABASE_URL is None:
    raise EnvironmentError("DATABASE_URL environment variable is not defined.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database
def initialize_database():
    print("Database initializing...")
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

# Call the database initialization function
initialize_database()

# Allow CORS for all domains in this example
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(login.router, prefix="", tags=["Authentication"])
app.include_router(react.router, prefix="", tags=["React"])
app.include_router(react_1.router, prefix="", tags=["React_1"])
app.include_router(admin.router, prefix="", tags=["Admin"])
app.include_router(user.router, prefix="", tags=["User"])



# Main function to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000)


