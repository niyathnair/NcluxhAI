from fastapi import FastAPI
from api.router.story import create, query
from core.logger import LOGGER

app = FastAPI(
    title="StoryVerse API",
    description="Story Generation and Management API",
    version="1.0.0"
)

# Include routers
app.include_router(create.router, prefix="/api/v1", tags=["story"])
app.include_router(query.router, prefix="/api/v1", tags=["story"])

@app.on_event("startup")
async def startup_event():
    LOGGER.info("Starting StoryVerse API")