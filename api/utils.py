from core.logger import LOGGER
from database import story_collection
from old_files.models import StoryStatus
from s1_script_gen import script_generator
from s2_image_gen import image_generator
from s3_audio_gen import getAudioElevenLabs
from s4_video_gen import create_video, load_language_fonts
from bson import ObjectId


async def run_remaining_steps(story_id: str):
    try:
        # Retrieve story from database
        story = await story_collection.find_one({"story_id": story_id})
        if not story:
            raise Exception(f"Story with id {story_id} not found")

        # Update story status in database
        await story_collection.update_one(
            {"story_id": story_id},
            {"$set": {"status": StoryStatus.SCRIPT_GENERATION_IN_PROGRESS}},
        )

        language = story.get("language")
        topic = story.get("topic")
        genre = story.get("genre")
        duration = story.get("duration")
        style = story.get("style")

        LOGGER.info(f"Generating script for story ID: {story_id}...")
        script_data = await script_generator(
            story_id, language, topic, genre, duration, style
        )

        # Update script_data in the database
        await story_collection.update_one(
            {"_id": ObjectId(story_id)},
            {
                "$set": {
                    "script_data": script_data,
                    "status": StoryStatus.SCRIPT_GENERATED,
                }
            },
        )

        await story_collection.update_one(
            {"story_id": story_id},
            {"$set": {"status": StoryStatus.VIDEO_GENERATION_IN_PROGRESS}},
        )

        # Step 2: Generate images using Flux
        LOGGER.info(f"Generating images with Flux for story ID {story_id}...")
        await image_generator(story_id, "flux")

        # Step 3: Generate audio
        LOGGER.info("Generating audio...")
        audio_result = await getAudioElevenLabs(story_id)
        if audio_result != "audio, SFX, and BGM generated":
            raise Exception(f"Audio generation failed: {audio_result}")

        # Step 4: Create video with Flux images
        LOGGER.info(f"Creating video with Flux images for story ID {story_id}...")
        language_fonts_config = load_language_fonts("languages/languages.json")
        video_result = await create_video(
            story_id, story["language"], "flux", language_fonts_config
        )
        if video_result != "success":
            raise Exception(f"Video creation failed: {video_result}")

        # Update story status in database
        await story_collection.update_one(
            {"story_id": story_id},
            {"$set": {"status": StoryStatus.VIDEO_GENERATED_SUCCESSFULLY}},
        )

        LOGGER.info("Complete flow finished successfully!")
    except Exception as e:
        LOGGER.error(f"An error occurred: {str(e)}")
        # Update story status and error in database
        await story_collection.update_one(
            {"story_id": story_id},
            {"$set": {"status": StoryStatus.FAILED, "error": str(e)}},
        )


async def async_generating_script(story_id: str):
    # Retrieve story details from the database
    story = await story_collection.find_one({"story_id": story_id})
    if not story:
        raise Exception(f"Story with id {story_id} not found")

    # Update story status in database
    await story_collection.update_one(
        {"story_id": story_id},
        {"$set": {"status": StoryStatus.SCRIPT_GENERATION_IN_PROGRESS}},
    )

    language = story.get("language")
    topic = story.get("topic")
    genre = story.get("genre")
    duration = story.get("duration")
    style = story.get("style")

    try:
        LOGGER.info(f"Generating script for story ID: {story_id}...")
        script_data = await script_generator(
            story_id, language, topic, genre, duration, style
        )

        # Update script_data in the database
        await story_collection.update_one(
            {"_id": ObjectId(story_id)},
            {
                "$set": {
                    "script_data": script_data,
                    "status": StoryStatus.SCRIPT_GENERATED,
                }
            },
        )

    except Exception:
        LOGGER.info(f"Error generating story for story ID: {story_id}")

        # Update script_data in the database
        await story_collection.update_one(
            {"_id": ObjectId(story_id)},
            {
                "$set": {
                    "script_data": script_data,
                    "status": StoryStatus.FAILED,
                }
            },
        )
