import json
from bson import ObjectId, json_util
from pydantic import BaseModel
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from config import config
from config.const_msg import TextMessages
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

    async def create_company(self, entity: CreateCompanyModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(entity.password)

            # Create an instance of CompanyModel without storing the plaintext password
            company_entity = CompanyModel(
                company_name=entity.company_name,
                company_uname=entity.company_uname,
                company_email=entity.company_email,
                backup_email=entity.backup_email,
                manager_email=entity.manager_email,
                first_name=entity.first_name,
                last_name=entity.last_name,
                hash_password=hashed_password,
                projectDetails=entity.projectDetails
            )

            # Convert Pydantic model instance to a dictionary
            company_dict = company_entity.dict()

            # Insert the dictionary into the collection
            result = await self.__collection.insert_one(company_dict)

            action_result.data = result.inserted_id
            action_result.message = TextMessages.INSERT_SUCCESS
        except Exception as e:
            action_result.status = False
            print(e)
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result


