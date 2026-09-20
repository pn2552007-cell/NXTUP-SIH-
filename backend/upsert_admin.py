import sys
import os
import getpass

# Add the backend dir to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import User
from app.auth.jwt_handler import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set.")
    print("Ensure you are running this in the Render Shell where environment variables are loaded.")
    sys.exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'LOCAL DB'}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

TARGET_EMAIL = "pn2552007@gmail.com"
ADMIN_ROLE = "ADMIN"

print("\n--- NXTUP Admin Account Setup ---")
print(f"Target Email: {TARGET_EMAIL}")
print("Please enter the new admin password. It will not be shown on screen.")
ADMIN_PASSWORD = getpass.getpass("Password: ")
if not ADMIN_PASSWORD:
    print("ERROR: Password cannot be empty.")
    sys.exit(1)

try:
    user = db.query(User).filter(User.email == TARGET_EMAIL).first()
    
    if user:
        print(f"User {TARGET_EMAIL} found. Current role: {user.role}")
        user.role = ADMIN_ROLE
        user.hashed_password = get_password_hash(ADMIN_PASSWORD)
        print("Updating user role to ADMIN and setting new password...")
    else:
        print(f"User {TARGET_EMAIL} not found.")
        user = User(
            email=TARGET_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            role=ADMIN_ROLE,
            full_name="System Administrator"
        )
        db.add(user)
        print("Creating new user with ADMIN role...")
    
    db.commit()
    print("Database operation completed successfully. Account is active.")
    
except Exception as e:
    db.rollback()
    print(f"An error occurred: {e}")
finally:
    db.close()
