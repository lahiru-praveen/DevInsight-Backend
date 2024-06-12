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
import smtplib
from email.mime.text import MIMEText
import uuid
import requests

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

            company_entity = CompanyModel(
                company_name=entity.company_name,
              
                admin_email=entity.admin_email,
                company_address=entity.company_address,
                phone_number=entity.phone_number,
                has_custom_domain=entity.has_custom_domain,
                domain=entity.domain,
               
                hash_password=hashed_password,
                email_verified=False
            )

            company_dict = company_entity.dict(by_alias=True)
            result = await self.__collection.insert_one(company_dict)

            action_result.data = result.inserted_id
            action_result.message = "Insert successful"
        except Exception as e:
            action_result.status = False
            action_result.message = "Action failed"
        finally:
            return action_result
        
    async def check_email(self, email: str) -> bool:
        try:
            result = await self.__collection.find_one({"admin_email": email})
            return result is not None
        except Exception as e:
            print(e)
            return False
        
    async def check_email(self, email: str) -> bool:
        try:
            result = await self.__collection.find_one({"admin_email": email})
            return result is not None
        except Exception as e:
            print(e)
            return False

    # Add the check_username method
    async def check_username(self, username: str) -> bool:
        try:
            result = await self.__collection.find_one({"company_uname": username})
            return result is not None
        except Exception as e:
            print(e)
            return False
        

    def send_verification_email(self, email: str, token: str):
        verification_link = f"http://127.0.0.1:8000/verify-email?token={token}"
        msg = MIMEText(f"Please verify your email by clicking the following link: {verification_link}")
        msg['Subject'] = 'Email Verification'
        msg['From'] = 'no-reply@yourdomain.com'
        msg['To'] = email

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('devinsightlemon@gmail.com', 'pnml qaak jdsa xphz')
            server.sendmail(msg['From'], [msg['To']], msg.as_string())

    # def send_verification_email(self, email: str, token: str):
    #     verification_link = f"http://127.0.0.1:8000/verify-email?token={token}"
    #     message = f"Please verify your email by clicking the following link: {verification_link}"

    #     return requests.post(
    #         "https://api.mailgun.net/v3/sandboxdf0f57c3ac5d4db08eea12d13d8752d8.mailgun.org/messages",
    #         auth=("api", "05d59a000d63086b94e81876253ed87c-a4da91cf-035c6b67"),
    #         data={
    #             "from": "no-reply@yourdomain.com",
    #             "to": [email],
    #             "subject": "Email Verification",
    #             "text": message
    #         }
    #     )


    async def get_company_by_token(self, token: str):
        try:
            result = await self.__collection.find_one({"verification_token": token})
            return result
        except Exception as e:
            print(e)
            return None

    async def verify_company_email(self, company_id: str):
        try:
            result = await self.__collection.update_one(
                {"_id": ObjectId(company_id)},
                {"$set": {"email_verified": True, "verification_token": None, "token_expiration": None}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(e)
            return False