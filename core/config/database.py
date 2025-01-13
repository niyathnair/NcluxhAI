from mongoengine import connect, disconnect
from core.logger import LOGGER
from dotenv import load_dotenv
import os
import motor.motor_asyncio

load_dotenv()

MODE = os.getenv("MODE", "development")
DATABASE_NAME = "storyverse"

if MODE == "production":
    MONGO_DETAILS = os.getenv("MONGODB_URI")
    if not MONGO_DETAILS:
        raise ValueError(
            "MONGODB_URI environment variable is not set for production mode"
        )
else:
    MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")


async def init_db():
    try:
        # Close any existing connections
        disconnect()

        # Create async client
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
        database = client[DATABASE_NAME]

        # Also connect mongoengine (needed for models)
        connect(db=DATABASE_NAME, host=MONGO_DETAILS)

        # Test the connection
        await client.admin.command("ping")

        LOGGER.info("Database connection established successfully.")
        return database
    except Exception as e:
        LOGGER.error(f"Error initializing database: {str(e)}")
        raise