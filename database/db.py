import datetime
import json
from bson import ObjectId, json_util
from pydantic import BaseModel, ValidationError
from pymongo import DESCENDING
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from config import config
from config.const_msg import TextMessages
from database.aggregation import get_next_operator_id_pipeline
from models.action_result import ActionResult
from passlib.context import CryptContext
from models.code_context_data import CodeContextData
from models.company_data_1 import CreateCompanyModel
from models.company_data_2 import CompanyModel

class DatabaseConnector:
    def __init__(self, collection_name: str):
        self.__connection_string = config.Configurations.mongo_db_url
        self.__database_name = 'dev-insight'
        self.__client = motor.motor_asyncio.AsyncIOMotorClient(self.__connection_string)
        try:
            self.__client.server_info()
            self.__database = self.__client.get_database(self.__database_name)
            self.__collection = self.__database.get_collection(collection_name)
            self.__delete_collection1 = self.__database.get_collection("delete_code_records")
            self.__delete_collection2 = self.__database.get_collection("delete_review_records")
        except ServerSelectionTimeoutError as e:
            raise Exception("Database connection timed out", e)

    async def run_aggregation(self, pipeline: list) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.aggregate(pipeline).to_list(None)
            action_result.data = result
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def add_code(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            next_id_cursor = self.__collection.aggregate(get_next_operator_id_pipeline)
            next_id_doc = await next_id_cursor.to_list(length=1)
            next_p_id = next_id_doc[0]['next_p_id'] if next_id_doc else 1

            entity_dict = entity.dict(by_alias=True, exclude={"id"})
            entity_dict['p_id'] = next_p_id

            result = await self.__collection.insert_one(entity_dict)
            action_result.data = str(result.inserted_id)
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)
        finally:
            return action_result

    async def delete_code(self, entity_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            document = await self.__collection.find_one({"p_id": entity_id})
            print(document)  # Debugging line to ensure document is found
            if document:
                delete_result = await self.__collection.delete_one({"p_id": entity_id})
                if delete_result.deleted_count == 1:
                    document["deleted_at"] = datetime.datetime.utcnow()  # Add deletion timestamp
                    await self.__delete_collection1.insert_one(document)
                    action_result.message = TextMessages.DELETE_SUCCESS
                else:
                    action_result.status = False
                    action_result.message = TextMessages.ACTION_FAILED
            else:
                action_result.status = False
                action_result.message = TextMessages.ACTION_FAILED
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error deleting code: {e}")
        finally:
            return action_result

    async def get_all_codes(self) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({}):
                if 'p_id' in document and document['p_id'] is not None:
                    json_doc = json.loads(json_util.dumps(document))
                    try:
                        documents.append(CodeContextData(**json_doc))
                    except ValidationError as validation_error:
                        print(f"Validation error for document {document['_id']}: {validation_error}")
                else:
                    print(f"Document missing required field 'p_id': {document}")
            action_result.data = documents
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)
        finally:
            return action_result

    async def get_latest_p_id(self) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            # Assuming your collection has a field indicating insertion order or using the default _id
            latest_entity = await self.__collection.find_one({}, sort=[("p_id", DESCENDING)])
            if latest_entity is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                action_result.data = latest_entity.get("p_id")
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def get_all_project_names(self) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            project_names = await self.__collection.distinct("p_name")
            action_result.data = project_names
            action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def create_company(self, entity: CreateCompanyModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(entity.password)
            company_entity = CompanyModel(
                company_name=entity.company_name,
                company_uname=entity.company_uname,
                company_email=entity.company_email,
                backup_email=entity.backup_email,
                manager_email=entity.manager_email,
                first_name=entity.first_name,
                last_name=entity.last_name,
                hash_password=hashed_password,
                projectDetails=entity.projectDetails)
            company_dict = company_entity.dict()
            result = await self.__collection.insert_one(company_dict)
            action_result.data = str(result.inserted_id)  # Convert ObjectId to string
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error creating company: {e}")
        finally:
            return action_result

    async def add_review(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.insert_one(entity.model_dump(by_alias=True, exclude=["id"]))
            action_result.data = str(result.inserted_id)  # Convert ObjectId to string
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error adding review: {e}")
        finally:
            return action_result

    async def get_review_by_id(self, entity_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": entity_id})
            if entity is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                json_data = json.loads(json_util.dumps(entity))
                action_result.data = json_data
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result

    async def delete_review(self, entity_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            document = await self.__collection.find_one({"p_id": entity_id})
            print(document)  # Debugging line to ensure document is found
            if document:
                delete_result = await self.__collection.delete_one({"p_id": entity_id})
                if delete_result.deleted_count == 1:
                    document["deleted_at"] = datetime.datetime.utcnow()  # Add deletion timestamp
                    await self.__delete_collection2.insert_one(document)
                    action_result.message = TextMessages.DELETE_SUCCESS
                else:
                    action_result.status = False
                    action_result.message = TextMessages.ACTION_FAILED
            else:
                action_result.status = False
                action_result.message = TextMessages.ACTION_FAILED
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error deleting code: {e}")
        finally:
            return action_result

    async def add_request(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            get_next_request_id_pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "next_request_id": {"$max": "$request_id"}
                    }
                },
                {
                    "$project": {
                        "next_request_id": {"$ifNull": [{"$add": ["$next_request_id", 1]}, 1]}
                    }
                }
            ]
            next_id_cursor = self.__collection.aggregate(get_next_request_id_pipeline)
            next_id_doc = await next_id_cursor.to_list(length=1)
            next_request_id = next_id_doc[0]['next_request_id'] if next_id_doc else 1

            entity_dict = entity.dict(by_alias=True, exclude={"id"})
            entity_dict['request_id'] = next_request_id

            result = await self.__collection.insert_one(entity_dict)
            action_result.data = str(result.inserted_id)
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)
        finally:
            return action_result

    async def get_request_by_id(self, entity_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": entity_id})
            if entity is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                json_data = json.loads(json_util.dumps(entity))
                action_result.data = json_data
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result
