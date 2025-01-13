import asyncio
from fastapi import FastAPI
from core.logger import LOGGER
from core.config.database import init_db
from core.utils.redis import redis_client
from core.config.redis import CHANNELS
from api.router import story_create
from agentcrew.story_writer_agent.main import StoryWriterAgent
from agentcrew.director_agent.main import DirectorAgent
from core.events.consumer import initialize_consumer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Story Writer API",
    description="API for generating stories",
    version="0.1.0",
)

app.include_router(story_create.router)


async def initialize_redis():
    for _ in range(3):  # Try 3 times
        try:
            await redis_client.ping()  # Test the connection
            LOGGER.info("Redis instance connected")
            return redis_client
        except Exception as e:
            LOGGER.error(f"Failed to connect to Redis: {e}")
            await asyncio.sleep(2)  # Wait for Redis to start
    return None


async def startup():
    # Initialize database
    init_db()

    # Initialize Redis
    # redis_client = await initialize_redis()
    # if redis_client is None:
    #     LOGGER.error("Failed to start Redis after multiple attempts.")
    #     return

    # Initialize agents
    story_writer = StoryWriterAgent()
    director = DirectorAgent()

    # Initialize the event consumer
    # initialize_consumer(story_writer, director)


app.add_event_handler("startup", startup)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
