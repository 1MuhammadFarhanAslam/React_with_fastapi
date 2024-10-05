# from fastapi import FastAPI
# import os
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from fastapi.middleware.cors import CORSMiddleware
# from routers import admin, user, login, react, react_ttm, Forgot_password
from react_database import is_server_available

# app = FastAPI()


# # Get the database URL from the environment variable
# DATABASE_URL = os.environ.get("DATABASE_URL")
# # Check if DATABASE_URL is defined
# if DATABASE_URL is None:
#     raise EnvironmentError("DATABASE_URL environment variable is not defined.")

# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Initialize the database
# def initialize_database_and_check_server_availability():
#     print("---------------------------------------------------------------")
#     print("---------------------Database initializing-------------------")
#     print("---------------------------------------------------------------")
#     from models import Base
#     Base.metadata.create_all(bind=engine)
#     print("---------------------Database initialized successfully--------")
#     print("---------------------------------------------------------------")
#     print("---------------------Checking if the server is available--------")

#     # Define the URL of the Nginx server to check if it is available
#     nginx_url = "https://api.bittaudio.ai/" 

#     # Call the function outside of the endpoint
#     server_available = is_server_available(nginx_url)
#     if server_available:
#         print("---------------------------------------------------------------")
#         print("---------------------Server is available-------------------")
#         print("---------------------------------------------------------------")
#     else:
#         print("---------------------------------------------------------------")
#         print("---------------------Server is not available-------------------")
#         print("---------------------------------------------------------------")  

# # Call the database initialization function
# initialize_database_and_check_server_availability()


# # # Allow CORS only if not handled by Nginx
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=origins,
# #     allow_credentials=True, 
# #     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
# #     allow_headers=["*"],
# #     expose_headers=["*"],
# # )

# # Define the list of allowed origins
# origins = [
#     # "http://127.0.0.1:3000",
#     # "http://193.29.187.81:8000",
#     # "http://bittaudio.ai",
#     # "http://api.bittaudio.ai",
#     "https://bittaudio.ai",
#     "https://api.bittaudio.ai",
#     "http://v1.api.bittaudio.ai",
#     "https://v1.api.bittaudio.ai",
#     "http://149.36.1.168:41981",
# ]


# # Allow CORS for all origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["DNT", "User-Agent", "X-Requested-With", "If-Modified-Since", "Cache-Control", "Content-Type", "Range", "Authorization", "On-behalf-of", "x-sg-elas-acl" ],
#     expose_headers=["*"],
# )

# # Include routers
# app.include_router(login.router, prefix="", tags=["Admin_Authentication"])
# app.include_router(admin.router, prefix="", tags=["Admin_Management"])
# # app.include_router(user.router, prefix="", tags=["User"])
# app.include_router(react.router, prefix="", tags=["Frontend_Signup/Login"])
# # app.include_router(react_1.router, prefix="", tags=["React_1"])
# app.include_router(Forgot_password.router, prefix="", tags=["Forgot_Password"])  
# app.include_router(react_ttm.router, prefix="", tags=["Text-To-Music"])




# # Main function to run the FastAPI app
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port= 8000)


from fastapi import FastAPI
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, user, login, react, react_ttm, Forgot_password
# from react_database import is_server_available

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
def initialize_database_and_check_server_availability():
    print("---------------------------------------------------------------")
    print("---------------------Database initializing-------------------")
    print("---------------------------------------------------------------")
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("---------------------Database initialized successfully--------")
    print("---------------------------------------------------------------")
    print("---------------------Checking if the server is available--------")

    # Define the URL of the Nginx server to check if it is available
    # nginx_url =  "https://api.bittaudio.ai/" 
    nginx_url =  "http://213.136.80.78:8000/"

    # Call the function outside of the endpoint
    server_available = is_server_available(nginx_url)
    if server_available:
        print("---------------------------------------------------------------")
        print("---------------------Server is available-------------------")
        print("---------------------------------------------------------------")
    else:
        print("---------------------------------------------------------------")
        print("---------------------Server is not available-------------------")
        print("---------------------------------------------------------------")  

# Call the database initialization function
initialize_database_and_check_server_availability()

# Define the list of allowed origins
origins = [
    "http://localhost:3000",    # Allow this origin to access the API just for development/testing
    "http://127.0.0.1:3000",
    "https://bittaudio.ai",
    "https://api.bittaudio.ai",
    "https://api.bittaudio.ai/api/ttm_endpoint",
    "http://v1.api.bittaudio.ai",
    "https://v1.api.bittaudio.ai",
    "http://149.36.1.168:41981",
    "http://38.242.218.205:8000",
    "http://213.136.80.78:8000",
    "http://89.187.159.41:40191"
]

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["DNT", "User-Agent", "X-Requested-With", "If-Modified-Since", "Cache-Control", "Content-Type", "Range", "Authorization", "On-behalf-of", "x-sg-elas-acl" ],
    expose_headers=["*"],
)

# Include routers
app.include_router(login.router, prefix="", tags=["Admin_Authentication"])
app.include_router(admin.router, prefix="", tags=["Admin_Management"])
app.include_router(react.router, prefix="", tags=["Frontend_Signup/Login"])
app.include_router(Forgot_password.router, prefix="", tags=["Forgot_Password"])  
app.include_router(react_ttm.router, prefix="", tags=["Text-To-Music"])

# Main function to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

