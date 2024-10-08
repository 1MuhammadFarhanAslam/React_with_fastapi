import re
import datetime
from admin_database import (
    get_admin,
    update_admin_password,
    delete_admin_by_username)

from user_database import create_user , get_user, assign_user_roles, update_user_password, UserRole
from hashing import hash_password, verify_hash
from models import Admin , User, Role
from admin_auth import get_current_active_admin
from admin_database import get_secret_key, get_database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.logger import logger



router = APIRouter()

class RoleAlreadyExists(HTTPException):
    def __init__(self, status_code: int = 400, detail: str = "Role Already exists."):
        self.status_code = status_code
        self.detail = detail

class UserNotFound(HTTPException):
    def __init__(self, status_code: int = 400, detail: str = "User not found."):
        self.status_code = status_code
        self.detail = detail


@router.post("/admin/create", response_model=dict, tags=["Admin_Management"])
async def create_admin_account(
    secret_key: str = Form(...),
    username: str = Form(...), 
    enter_password: str = Form(..., min_length=8, max_length=16, regex="^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?/~\\-=|\\\\]+$"),
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)
):
    try:
        print("username:" , username)
        print("enter_password:" , enter_password)

        # Get the secret key from the database
        actual_secret_key = get_secret_key(db)

        # Check if the provided secret key matches the actual secret key
        if secret_key != actual_secret_key:
            raise HTTPException(status_code=401, detail="Invalid secret key")

        # Validate that both username and password are provided
        if not username or not enter_password:
            raise HTTPException(status_code=400, detail="Both username and password are required.")

        # Check if the username already exists
        existing_admin = db.query(Admin).filter(Admin.username == username).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Username already exists.")

        # Additional validation: Check if the password meets the specified conditions
        if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", enter_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

        print(f"Creating admin with username: {username}")
        # Hash the password
        hashed_password = hash_password(enter_password)
        
        # Create the admin instance with hashed_password
        new_admin = Admin(username=username, hashed_password=hashed_password)
        
        # Add the new admin to the session and commit
        db.add(new_admin)
        db.commit()
        
        print(f"Admin created successfully: {username}")
        
        # Return the created admin instance
        return {
            "message": "Admin created successfully",
            "admin_info": {
                "id": new_admin.id,
                "username": new_admin.username,
                "password": new_admin.hashed_password,
                "admin_flag": new_admin.admin_flag,
                "created_at": new_admin.created_at
            }
        }
    except HTTPException as e:
        raise e  # Re-raise HTTPException to return specific error response
    except Exception as e:
        # Log the error and return a generic error response
        print(f"Error during admin creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    

@router.get("/admin/read", response_model=None, tags=["Admin_Management"])
async def read_all_admins_info(
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)
):
    try:
        logger.info("Attempting to retrieve all admins")
        admins = db.query(Admin).all()  # Assuming your SQLAlchemy model is named 'Admin'
        logger.info(f"Retrieved admins: {admins}")

        # Reorder fields in the response body
        admins_data = []
        for admin in admins:
            admin_data = {
                "message": "Admin retrieved successfully",
                "admin_info": {
                    "id": admin.id,
                    "admin_flag": admin.admin_flag,
                    "username": admin.username,
                    "hashed_password": admin.hashed_password,
                    "created_at": admin.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
                }
            }
            admins_data.append(admin_data)

        return admins_data
    except Exception as e:
        logger.error(f"Error during admin retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@router.get("/admin/read/{username}", response_model=None, tags=["Admin_Management"])
async def read_admin_info(
    username: str, 
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)
):
    try:
        admin = db.query(Admin).filter(Admin.username == username).first()
        if admin:
            logger.info(f"Admin found: {admin}")
            
            # Customizing the response body
            admin_data = {
                "message": "Admin retrieved successfully",
                "admin_info": {
                    "id": admin.id,
                    "admin_flag": admin.admin_flag,
                    "username": admin.username,
                    "hashed_password": admin.hashed_password,
                    "created_at": admin.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")
                }
            }
            
            return admin_data
        else:
            logger.warning(f"Admin not found with username: {username}")
            raise HTTPException(status_code=404, detail="Admin not found")
    except Exception as e:
        logger.error(f"Error during admin retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/admin/{username}", response_model=dict, tags=["Admin_Management"])
async def update_admin(
    username: str,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_new_password: str = Form(...),
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)  # Pass the db dependency here
):

    try:
        # Validate that all required fields are provided
        if not username or not current_password or not new_password or not confirm_new_password:
            raise HTTPException(status_code=400, detail="All fields are required.")

        # Verify the password of the current admin
        if not verify_hash(current_password, current_active_admin.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid current password")

        # Ensure the new password is not the same as the old password
        if current_password == confirm_new_password:
            raise HTTPException(status_code=400, detail="New password must be different from the current password.")

        # Ensure that the retyped password and new password match
        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="New_Password and confirm_new_password do not match")
        
        # Additional validation: Check if the password meets the specified conditions
        if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", confirm_new_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

        # Hash the new password consistently
        hashed_password = hash_password(confirm_new_password)

        # Update the admin's password in the database
        update_admin_password(username, hashed_password, db)

        return {"message": "Password changed successfully"}

    except HTTPException as e:
        # Re-raise HTTPException to return specific error response
        raise e

    except Exception as e:
        # Log the error and return a generic error response
        logger.error(f"Error during admin update: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

@router.delete("/admin/delete/{username}", response_model=dict, tags=["Admin_Management"])
async def delete_admin(
    username: str,
    current_password: str = Form(..., min_length=8, max_length=16, regex="^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?/~\\-=|\\\\]+$"),
    retype_current_password: str = Form(...),
    current_active_admin: Admin = Depends(get_current_active_admin)
):
    try:
        existing_admin = get_admin(username)

        if not existing_admin:
            raise HTTPException(status_code=404, detail="Admin not found with the specified username")

        if not verify_hash(current_password, existing_admin.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")

        if current_password != retype_current_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        # Additional validation to prevent deleting the currently logged-in admin
        if existing_admin.username == current_active_admin.username:
            raise HTTPException(status_code=400, detail="Cannot delete currently logged-in admin")

        delete_admin_by_username(username)

        return {"message": "Admin deleted successfully"}

    except HTTPException as e:
        # Return the HTTPException directly
        raise e

    except Exception as e:
        # Log the error and return a generic error response
        logger.error(f"Error during admin deletion: {e}")
        # Return a generic error response
        raise HTTPException(status_code=500, detail="Internal Server Error")



# @router.post("/admin/create_users", response_model=dict, tags=["Admin_Management"])
# async def create_user_account(
#     username: str = Form(...),
#     set_password: str = Form(..., min_length=8, max_length=16, regex="^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;<>,.?/~\\-=|\\\\]+$"),
#     selected_role: str = Form(...),  # Admin-selected role for the user
#     subscription_duration_in_days: int = Form(...),  # Subscription duration in days or minutes
#     current_active_admin: Admin = Depends(get_current_active_admin),
#     db: Session = Depends(get_database)
# ):
#     try:
#         if not username or not set_password:
#             raise HTTPException(status_code=400, detail="Both username and password are required.")

#         if subscription_duration_in_days <= 0:
#             raise HTTPException(status_code=400, detail="Subscription duration must be greater than 0.")

#         # Additional validation: Check if the password meets the specified conditions
#         if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", set_password):
#             raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

#         # Create the user and get user info
#         user_info = create_user(username=username, password=set_password, role_assign=selected_role,
#                                 subscription_duration_in_days=subscription_duration_in_days)

#         if user_info is None:
#             raise HTTPException(status_code=400, detail="Username already exists. Please choose a different username.")

#         return {"message": "User created successfully", "user_info": user_info}

#     except HTTPException as e:
#         print(f"Error during user creation: {e}")
#         raise e
#     except Exception as e:
#         print(f"Error during user creation: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post("/admin/create_users", response_model=dict, tags=["Admin_Management"])
async def create_user_account(
    selected_role: UserRole,  # Use UserRole Enum for selected_role
    username: str = Form(...),
    set_password: str =  Form(...),
    subscription_duration_in_days: int = Form(...),
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)
):
    try:

        if not username or not set_password:
            raise HTTPException(status_code=400, detail="Both username and password are required.")

        if subscription_duration_in_days <= 0:
            raise HTTPException(status_code=400, detail="Subscription duration must be greater than 0.")
        
        # Additional validation: Check if the password meets the specified conditions
        if not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", set_password):
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")

        # Create the user and get user info
        user_info = create_user(username=username, password=set_password, role_assign=selected_role,
                                subscription_duration_in_days=subscription_duration_in_days)

        if user_info is None:
            raise HTTPException(status_code=400, detail="Username already exists.")

        return {"message": "User created successfully", "user_info": user_info}
    
    except HTTPException as e:
        print(f"Error during user creation: {e}")
        raise e

    
@router.post("/admin/modify_user_roles", tags=["Admin_Management"])
async def modify_user_roles(
    selected_role: UserRole,  # Admin-selected role for the user
    username: str = Form(...),
    subscription_duration: int = Form(...),  # Subscription duration in days or minutes
    current_active_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_database)
):
    try:
        if not username:
            raise HTTPException(status_code=400, detail="Username is required.")

        # Fetch the user details
        user = db.query(User).filter(User.username == username).first()

        if user is None:
            raise UserNotFound()

        # # Validate the role syntax before proceeding
        # role_details = get_role_details(selected_role)
        # if role_details is None:
        #     raise HTTPException(status_code=400, detail=f"Invalid role syntax: {selected_role}")
        
        # check if selected_role already exists and subscription_end_time for that selected_role has not expired
        existing_role = db.query(Role).filter(Role.username == username, Role.role_name == selected_role).first()
        if existing_role and existing_role.subscription_end_time > datetime.datetime.now():
            raise RoleAlreadyExists()

        # Assign the modified role to the user with the specified subscription duration
        assign_user_roles(username, selected_role, subscription_duration)

        # Fetch the updated user details after role modification
        updated_user = db.query(User).filter(User.username == username).first()
        updated_user_roles = db.query(Role).filter(Role.username == username).all()

        if updated_user is None:
            raise HTTPException(status_code=400, detail="Error retrieving updated user details.")
        if updated_user_roles is None:
            raise HTTPException(status_code=400, detail="Error retrieving updated user roles.")

        return {"message": f"Role for user '{username}' modified successfully", "user_info": updated_user, "roles": updated_user_roles}
    
    except UserNotFound:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
    
    except RoleAlreadyExists:
        raise HTTPException(status_code=400, detail=f"User '{username}' already has the selected role '{selected_role}'. Please wait until the subscription period expires for this role. Try update other roles.")
    

@router.post("/admin/reset_password/{username}", response_model=dict, tags=["Admin_Management"])
async def reset_user_password(
    username: str,
    new_password: str = Form(...),
    db: Session = Depends(get_database),
    current_active_admin: User = Depends(get_current_active_admin)
):
    try:
        # Check if the username exists in the database
        user = get_user(username, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Reset the password for the user
        if update_user_password(username, new_password, db):
            print(f"Password reset for user '{username}' was successful.")
            return {"message": "Password reset successful"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")

    except HTTPException as e:
        raise e  # Re-raise HTTPException to return a specific error response
    except Exception as e:
        print(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
