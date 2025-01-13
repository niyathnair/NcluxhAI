from core.logger import LOGGER
from mongoengine.errors import ValidationError, DoesNotExist, OperationError
from mongoengine import Document
from typing import Dict, List, Any, Optional, Type, TypeVar, Union
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import wraps

T = TypeVar("T", bound=Document)


class DatabaseManager:
    def __init__(self):
        self._retry_config = {
            "stop": stop_after_attempt(3),
            "wait": wait_exponential(multiplier=1, min=4, max=10),
        }

    def with_retry(self, func):
        @retry(stop=self._retry_config["stop"], wait=self._retry_config["wait"])
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    @property
    def create_document(self):
        @self.with_retry
        async def _create_document(self, document: T) -> Optional[str]:
            try:
                LOGGER.debug(f"Creating document of type {type(document).__name__}")
                document.save()
                LOGGER.info(f"Created document with ID: {document.id}")
                return str(document.id)
            except ValidationError as e:
                LOGGER.error(
                    f"Validation error creating document: {str(e)}", exc_info=True
                )
                raise
            except Exception as e:
                LOGGER.error(f"Error creating document: {str(e)}", exc_info=True)
                raise

        return _create_document.__get__(self, DatabaseManager)

    @property
    def read_document(self):
        @self.with_retry
        async def _read_document(
            self,
            model_class: Type[T],
            document_id: str,
            raise_if_not_found: bool = False,
        ) -> Optional[T]:
            try:
                LOGGER.debug(
                    f"Reading document {document_id} of type {model_class.__name__}"
                )
                document = model_class.objects.get(id=document_id)
                return document
            except DoesNotExist:
                msg = f"Document with id {document_id} not found"
                if raise_if_not_found:
                    LOGGER.error(msg)
                    raise
                LOGGER.warning(msg)
                return None
            except Exception as e:
                LOGGER.error(f"Error reading document: {str(e)}", exc_info=True)
                raise

        return _read_document.__get__(self, DatabaseManager)

    @property
    def update_document(self):
        @self.with_retry
        async def _update_document(
            self,
            model_class: Type[T],
            document_id: str,
            update_data: Dict[str, Any],
            upsert: bool = False,
        ) -> bool:
            try:
                LOGGER.debug(f"Updating document {document_id} of type {model_class.__name__}")
                LOGGER.debug(f"Update data: {update_data}")
                if 'outline' in update_data:
                    LOGGER.debug(f"Outline content: {vars(update_data['outline'])}")
                    scenes = getattr(update_data['outline'], 'scenes', [])
                    LOGGER.debug(f"Number of scenes: {len(scenes)}")
                    for i, scene in enumerate(scenes):
                        LOGGER.debug(f"Scene {i} content: {vars(scene)}")
                        LOGGER.debug(f"Scene {i} characters: {getattr(scene, 'characters_present', 'None')}")
                        LOGGER.debug(f"Scene {i} actions: {getattr(scene, 'character_actions', 'None')}")
                result = model_class.objects(id=document_id).update_one(
                    upsert=upsert, **update_data
                )
                if result:
                    LOGGER.info(f"Updated document {document_id}")
                    return True
                return False
            except Exception as e:
                LOGGER.error(f"Error updating document: {str(e)}", exc_info=True)
                raise

        return _update_document.__get__(self, DatabaseManager)

    @property
    def delete_document(self):
        @self.with_retry
        async def _delete_document(
            self, model_class: Type[T], document_id: str
        ) -> bool:
            try:
                LOGGER.debug(
                    f"Deleting document {document_id} of type {model_class.__name__}"
                )
                result = model_class.objects(id=document_id).delete()
                if result:
                    LOGGER.info(f"Deleted document {document_id}")
                    return True
                return False
            except Exception as e:
                LOGGER.error(f"Error deleting document: {str(e)}", exc_info=True)
                raise

        return _delete_document.__get__(self, DatabaseManager)
# Create a singleton instance
db_manager = DatabaseManager()
