from fastapi import FastAPI, Request
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, login, react, react_ttm, Forgot_password
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

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
    print("---------------------Database initializing-------------------")
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("---------------------Database initialized successfully--------")

# Call the database initialization function
initialize_database()

#Allow CORS for only the React frontend server
# origins = [
#     "http://85.239.241.96:3000",  # Your React frontend server's HTTP URL
#     "http://api.bittaudio.ai",
#     "http://144.91.69.154:8000",
#     "http://localhost:3000",
#     "http:127.0.0.1:3000",
#     "http://89.37.121.214:44107",
#     "http://149.11.242.18:14428",
#     "http://bittaudio.ai",
#     "http://v1.bittaudio.ai",
#     "http://v2.bittaudio.ai",
# ]


# # Allow CORS only if not handled by Nginx
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )

# Define the list of allowed origins
origins = [
    "http://85.239.241.96:3000",  # Your React frontend server's HTTP URL
    "http://api.bittaudio.ai",
    "http://144.91.69.154:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://89.37.121.214:44107",
    "http://149.11.242.18:14428",
    "http://bittaudio.ai",
    "http://v1.bittaudio.ai",
    "http://v2.bittaudio.ai",
    "http://93.114.160.254:40321"
]

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle RateLimitExceeded exceptions globally and return a JSON response with a custom error message.

    Args:
        request (Request): The incoming request causing the rate limit exception.
        exc (RateLimitExceeded): The RateLimitExceeded exception object.

    Returns:
        JSONResponse: JSON response with status code 429 (Too Many Requests) and a custom error message.
    """
    return JSONResponse(
        status_code=429,
        content={"message": "Oops! ☠️💀☠️💀 You have exceeded the rate limit: 5/minute. Please try again later......."})


# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["DNT", "User-Agent", "X-Requested-With", "If-Modified-Since", "Cache-Control", "Content-Type", "Range", "Authorization", "On-behalf-of", "x-sg-elas-acl" ],
    expose_headers=["*"],
)

# Include routers
app.include_router(login.router, prefix="", tags=["Admin_Authentication"])
app.include_router(admin.router, prefix="", tags=["Admin_Management"])
# app.include_router(user.router, prefix="", tags=["User"])
app.include_router(react.router, prefix="", tags=["Frontend_Signup/Login"])
# app.include_router(react_1.router, prefix="", tags=["React_1"])
app.include_router(Forgot_password.router, prefix="", tags=["Forgot_Password"])
app.include_router(react_ttm.router, prefix="", tags=["Text-To-Music"])




# Main function to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000)


