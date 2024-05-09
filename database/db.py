import json
from bson import ObjectId, json_util
from pydantic import BaseModel
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from config import config
from config.const_msg import TextMessages
from models.action_result import ActionResult
from models.code_context_data import CodeContextData


class DatabaseConnector:
    def __init__(self, collection_name: str):
        self.__connection_string = config.Configurations.mongo_db_url
        self.__database_name = 'dev-insight'
        self.__client = motor.motor_asyncio.AsyncIOMotorClient(self.__connection_string)
        try:
            self.__client.server_info()
            self.__database = self.__client.get_database(self.__database_name)
            self.__collection = self.__database.get_collection(collection_name)  # Initialize __collection here
        except ServerSelectionTimeoutError as e:
            raise Exception("Database connection timed out" , e)

    async def add_code(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.insert_one(entity.model_dump(by_alias=True, exclude=["id"]))
            action_result.data = result.inserted_id
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            print(e)
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def delete_code(self, entity_id: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            delete_result = await self.__collection.delete_one({"_id": ObjectId(entity_id)})
            if delete_result.deleted_count == 1:
                action_result.message = TextMessages.DELETE_SUCCESS
            else:
                action_result.status = False
                action_result.message = TextMessages.ACTION_FAILED
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def get_all_codes(self) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({}):
                json_doc = json.loads(json_util.dumps(document))
                documents.append(CodeContextData(**json_doc))
            action_result.data = documents
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result
        
    async def create_company(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.insert_one(entity.model_dump(by_alias=True, exclude=["id"]))
            action_result.data = result.inserted_id
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            print(e)
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result    