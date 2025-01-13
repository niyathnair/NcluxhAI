from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from core.config.database import story_collection
from core.models.story import StoryModel
from api.schemas.requests import UpdateCharactersRequest, UpdatePlacesObjectsRequest
from api.schemas.responses import UpdateCharactersResponse, UpdatePlacesObjectsResponse

router = APIRouter()


@router.put("/stories/{story_id}/characters", response_model=UpdateCharactersResponse)
async def update_characters(story_id: str, request: UpdateCharactersRequest):
    story = await story_collection.find_one({"story_id": story_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Update characters in the main structure
    await story_collection.update_one(
        {"story_id": story_id}, {"$set": {"characters": request.characters}}
    )

    # Update characters in the memory structure
    memory_characters = {char["name"]: char for char in request.characters}
    await story_collection.update_one(
        {"story_id": story_id}, {"$set": {"memory.characters": memory_characters}}
    )

    return UpdateCharactersResponse(
        success=True, data={"message": "Characters updated successfully"}
    )


@router.put(
    "/stories/{story_id}/places_objects", response_model=UpdatePlacesObjectsResponse
)
async def update_places_objects(story_id: str, request: UpdatePlacesObjectsRequest):
    story = await story_collection.find_one({"story_id": story_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Update places_objects in the main structure
    await story_collection.update_one(
        {"story_id": story_id}, {"$set": {"places_objects": request.places_objects}}
    )

    # Update places and objects in the memory structure
    memory_places = {
        place["name"]: place for place in request.places_objects.get("places", [])
    }
    memory_objects = {
        obj["name"]: obj for obj in request.places_objects.get("objects", [])
    }

    await story_collection.update_one(
        {"story_id": story_id},
        {"$set": {"memory.places": memory_places, "memory.objects": memory_objects}},
    )

    return UpdatePlacesObjectsResponse(
        success=True, data={"message": "Places and objects updated successfully"}
    )
