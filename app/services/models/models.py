from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL as SQLAlchemy_URL # Renamed to avoid potential naming conflicts
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # Needed for CREATE DATABASE

# --- Database Configuration from .env ---
# Ensure these are set in your .env file
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_HOST = config("DB_HOST", default="localhost")    # Default to 'localhost' if not set
DB_PORT = config("DB_PORT", default=5432, cast=int) # Default to 5432 if not set
DB_NAME = config("DB_NAME", default="medbot")       # Default to 'medbot' if not set

# --- Function to Ensure Database Exists ---
def ensure_database_exists():
    """
    Checks if the target database exists, and creates it if it doesn't.
    Requires the DB_USER to have CREATEDB privileges.
    """
    pg_conn = None
    try:
        # Connect to the default 'postgres' database to check/create the target database
        pg_conn = psycopg2.connect(
            dbname="postgres",  # Standard database to connect to for admin tasks
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with pg_conn.cursor() as cur:
            # Check if the target database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            exists = cur.fetchone()
            if not exists:
                print(f"Database '{DB_NAME}' does not exist. Attempting to create it...")
                cur.execute(f"CREATE DATABASE {DB_NAME}") # Using f-string for DB_NAME as it's from config
                print(f"Database '{DB_NAME}' created successfully.")
                # Optionally, grant privileges if the creator is a superuser and DB_USER is different
                # For simplicity, this example assumes DB_USER itself has necessary future rights
                # or they will be granted separately.
                # Example: cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO \"{DB_USER}\"")
            else:
                print(f"Database '{DB_NAME}' already exists.")

    except OperationalError as e:
        print(f"OperationalError during database check/creation: {e}")
        print(f"This might mean PostgreSQL server is not running, or '{DB_USER}' cannot connect to 'postgres' database, or lacks CREATEDB privilege.")
        print("Please ensure PostgreSQL is running and the user has appropriate permissions, or create the database manually.")
        # For a robust application, you might want to raise the error or exit here
    except Exception as e:
        print(f"An unexpected error occurred during database check/creation: {e}")
    finally:
        if pg_conn:
            pg_conn.close()

# --- Ensure Database Exists Before SQLAlchemy Setup ---
ensure_database_exists()

# --- SQLAlchemy Setup ---
# This will connect to the specific database (DB_NAME)
sqlalchemy_database_url = SQLAlchemy_URL.create(
    drivername="postgresql+psycopg2", # Specify psycopg2 as the driver for SQLAlchemy
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,  # Connect to your application's database
    port=DB_PORT
)

engine = create_engine(sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)

# --- Create Tables in the Database ---
# This attempts to create the tables defined above (e.g., "conversations")
# if they don't already exist in the connected database.
try:
    print(f"Attempting to create tables in database '{DB_NAME}' if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print(f"Tables checked/created successfully in database '{DB_NAME}'.")
except Exception as e:
    print(f"Error creating tables in database '{DB_NAME}' with SQLAlchemy: {e}")
    print("Please check your SQLAlchemy models and database connection.")
