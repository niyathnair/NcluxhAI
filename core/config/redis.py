import os

# Redis configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": os.getenv("REDIS_PORT", 6379),
    "password": os.getenv("REDIS_PASSWORD", ""),
    "db": 0,
    "decode_responses": True,
}

# Redis channels
CHANNELS = {
    "CREATE_STORY_OUTLINE": "CREATE_STORY_OUTLINE",
    "STORY_OUTLINE_CREATED": "STORY_OUTLINE_CREATED",
    "GENERATE_SCRIPT": "GENERATE_SCRIPT",
    "SCRIPT_GENERATED": "SCRIPT_GENERATED",
}
