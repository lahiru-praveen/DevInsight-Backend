import datetime
import json
from typing import Optional, List
from bson import ObjectId, json_util
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError
from pymongo import DESCENDING, ReturnDocument
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from pymongo.results import DeleteResult

from config import config
from config.const_msg import TextMessages
from database.aggregation import get_next_operator_id_pipeline
from models.action_result import ActionResult
from passlib.context import CryptContext
from models.code_context_data import CodeContextData
from models.company_data_1 import CreateCompanyModel
from models.company_data_2 import CompanyModel
from models.response_data import ResponseItem
from models.updatecompany_data import UpdateCompanyModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from models.member import MemberModel
from models.request_data import RequestItem
from models.response_data import ResponseItem,SendFeedback,UpdateResponseRequest
from models.request_data import AssignItem, UpdateRequestStatus, AssignForwardItem  # Ensure you have this model defined in models/request_data.py


class DatabaseConnector:
    def __init__(self, collection_name: str):
        self.__connection_string = config.Configurations.mongo_db_url
        self.__database_name = 'dev-insight'
        self.__client = motor.motor_asyncio.AsyncIOMotorClient(self.__connection_string)
        try:
            self.__client.server_info()
            self.__database = self.__client.get_database(self.__database_name)
            self.__collection = self.__database.get_collection(collection_name)
            self.__delete_collection_code = self.__database.get_collection("delete_code_records")
            self.__delete_collection_review = self.__database.get_collection("delete_review_records")
        except ServerSelectionTimeoutError as e:
            raise Exception("Database connection timed out", e)

    async def run_aggregation(self, pipeline: list, user: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            pipeline.insert(0, {"$match": {"user": user}})
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
            next_id_cursor = self.__collection.aggregate(get_next_operator_id_pipeline(entity.user))
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

    async def get_all_codes(self, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({"user": user}):
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

    async def get_latest_p_id(self, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            # Assuming your collection has a field indicating insertion order or using the default _id
            latest_entity = await self.__collection.find_one({"user":user}, sort=[("p_id", DESCENDING)])
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

    async def get_all_project_names(self, user: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            project_names = await self.__collection.distinct("p_name", {"user": user})
            action_result.data = project_names
            action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
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
            action_result.message = "Failed to create company."
            print(e)
        finally:
            return action_result

    async def delete_code(self, entity_id: int, user: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            document = await self.__collection.find_one({"p_id": entity_id, "user": user})
            if document:
                delete_result = await self.__collection.delete_one({"p_id": entity_id, "user": user})
                if delete_result.deleted_count == 1:
                    document["deleted_at"] = datetime.utcnow()  # Add deletion timestamp
                    await self.__delete_collection_code.insert_one(document)
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

    async def delete_review(self, entity_id: int, user: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            document = await self.__collection.find_one({"p_id": entity_id, "user": user})
            print(document)  # Debugging line to ensure document is found
            if document:
                delete_result = await self.__collection.delete_one({"p_id": entity_id, "user": user})
                if delete_result.deleted_count == 1:
                    document["deleted_at"] = datetime.utcnow()  # Add deletion timestamp
                    await self.__delete_collection_review.insert_one(document)
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
            print(f"Error deleting review: {e}")
        finally:
            return action_result

    async def delete_requests_by_submission(self, entity_id: int, user: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            delete_result: DeleteResult = await self.__collection.delete_many({"p_id": entity_id, "user": user})

            if delete_result.deleted_count > 0:
                action_result.message = TextMessages.DELETE_SUCCESS
            else:
                action_result.status = False
                action_result.message = TextMessages.ACTION_FAILED
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error deleting requests: {e}")
        finally:
            return action_result

    async def get_review_by_id(self, entity_id: int, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": entity_id, "user":user})
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

    async def get_code_by_id(self, entity_id: int, user:str,p_id) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": entity_id, "user":user})
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

    async def create_company(self, entity: CreateCompanyModel) -> ActionResult:
        from utilis.profile import hash_password
        action_result = ActionResult(status=True)
        try:
            serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
            verification_token = serializer.dumps(entity.admin_email, salt='email-confirm-salt')

            hashed_password = hash_password(entity.password)

            company_entity = CompanyModel(
                company_name=entity.company_name,
                admin_email=entity.admin_email,
                company_address=entity.company_address,
                phone_number=entity.phone_number,
                has_custom_domain=entity.has_custom_domain,
                domain=entity.domain,
                hash_password=hashed_password,
                email_verified=False,
                logo_url='data:image/jpeg;base64,/9j/4QgZRXhpZgAATU0AKgAAAAgABwESAAMAAAABAAEAAAEaAAUAAAABAAAAYgEbAAUAAAABAAAAagEoAAMAAAABAAIAAAExAAIAAAAfAAAAcgEyAAIAAAAUAAAAkYdpAAQAAAABAAAAqAAAANQAB6EgAAAnEAAHoSAAACcQQWRvYmUgUGhvdG9zaG9wIDIxLjIgKFdpbmRvd3MpADIwMjQ6MDc6MDkgMTk6NDE6MDQAAAAAAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAMigAwAEAAAAAQAAAMgAAAAAAAAABgEDAAMAAAABAAYAAAEaAAUAAAABAAABIgEbAAUAAAABAAABKgEoAAMAAAABAAIAAAIBAAQAAAABAAABMgICAAQAAAABAAAG3wAAAAAAAABIAAAAAQAAAEgAAAAB/9j/7QAMQWRvYmVfQ00AAf/uAA5BZG9iZQBkgAAAAAH/2wCEAAwICAgJCAwJCQwRCwoLERUPDAwPFRgTExUTExgRDAwMDAwMEQwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwBDQsLDQ4NEA4OEBQODg4UFA4ODg4UEQwMDAwMEREMDAwMDAwRDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDP/AABEIAKAAoAMBIgACEQEDEQH/3QAEAAr/xAE/AAABBQEBAQEBAQAAAAAAAAADAAECBAUGBwgJCgsBAAEFAQEBAQEBAAAAAAAAAAEAAgMEBQYHCAkKCxAAAQQBAwIEAgUHBggFAwwzAQACEQMEIRIxBUFRYRMicYEyBhSRobFCIyQVUsFiMzRygtFDByWSU/Dh8WNzNRaisoMmRJNUZEXCo3Q2F9JV4mXys4TD03Xj80YnlKSFtJXE1OT0pbXF1eX1VmZ2hpamtsbW5vY3R1dnd4eXp7fH1+f3EQACAgECBAQDBAUGBwcGBTUBAAIRAyExEgRBUWFxIhMFMoGRFKGxQiPBUtHwMyRi4XKCkkNTFWNzNPElBhaisoMHJjXC0kSTVKMXZEVVNnRl4vKzhMPTdePzRpSkhbSVxNTk9KW1xdXl9VZmdoaWprbG1ub2JzdHV2d3h5ent8f/2gAMAwEAAhEDEQA/AOoSlIpJKVKUpJJKVKUpJJKVKUpJJKVKUpJJKVKUpJJKVKUpJJKVKUpJJKVKUpJJKVKSSQSU/wD/0OoKSRSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSCSQSU//R6gpJFJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpIJJBJT/9LqCkkUklKSSSSUpJImAStSnojbaWW+u4b2h0bW6SJSU5aSnewU3W1zIqcW7j3A7q/h9FdbWLcl7qw4S2tsB0dt7nbv8xJTmpLYt6DXtPoWvD+wfDmn7g1yyTVcLvQ2H1t2z0/5Xx/d/P3/ALiSmKS16egs2A32uLzyK4a0f5wc5yhldEcxhfivNhaJNb4k/wBR42+7+skpy0lPHosybW1UiXO1k8Bo5c5azOg4+3322Od3LSGj5N2lJTjJK9n9LfiMNzHmykfSn6TZ/O9vte1UUlKSSSSUpIJJBJT/AP/T6gpJFJJSkkkklLO+ifguow/6JR/xbP8AqQuXd9E/BdRh/wBEo/4tn/UhJTz2UN2fa08OvAPzcxdMeCuayP8AlKz/AMMD/qmLpTwUlNDoRJ6ZUSSTLtSST9J3coT2j/nCw/8ABbvnDmIvQf8Akyr4u/6oqD//ABQM/wCI/i5JSXrRI6XkQSCQBoSDq5o7I9N9Xo17rG7tomXCZhD6oGuw3Nfoxz6w7WPabKw73fm+1BHQ+mO9wrJB1B3Hv80lI+kNb9tziOA+GkeBdY5E6q5wyMAAkA5AkAkTpGv3ofRmNryc6tuja3tY0eQ3gKfVv6R0/wD8MBJTdywHYtzTwa3D8CuWaZaD5BdVkf0e3+o78i5Vn0G/AfkSUukkkkpSQSSCSn//1OoKSRSSUpJJJJSzvon4LqMP+iUf8Wz/AKkLmCJEeK0aut21VMrFDSGNDQd51gR+4kpjm4OTTddmv2ei20Wn3HdtDm/m7VunhYWT1ezJx30Opa0WCC4OJj+zsCbE6vfjVip7PWrbozWHAfuzq16SnR6LXZV06tlrDW8F0tcII9zuyrvsb/zhYJ4r2fOHWf8AUqFvXrXNIppDHH855mP7DPpf56zC55f6hcfU3b9/fdzvSU9B1et9nTr2VtL3EAhjRJMOa7RqPisLMaljhDmsaCPAgBZdXXrGsAup3vH5zDAP9l30VBnXMlrnl1bXhxljZjaI+ju2u9RJSfpTgOoZ7O5fuHwDng/lRup1W2X4Lq2F4ZeC8gTtEfSd/JWKMi1uS7KrOywuc/xHu+kw8bmLRZ1923348u8WuEf9KElOlmODMS5x0ArcfwK5dohoHgFczepX5g2ECukGSwGSSP33e3/NVRJSkkkklKSCSQSU/wD/1eoKSRSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSCSQSU//W6gpJFJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpIJJBJT/9fqCkkUklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkkkklKSSSSUpJJJJSkgkkElP/0OoKSSUJKUklCUJKUklCUJKUklCUJKUklCUJKUklCUJKUklCUJKUklCUJKUklCUJKUkEoSSU/wD/2f/tEBJQaG90b3Nob3AgMy4wADhCSU0EJQAAAAAAEAAAAAAAAAAAAAAAAAAAAAA4QklNBDoAAAAAAOUAAAAQAAAAAQAAAAAAC3ByaW50T3V0cHV0AAAABQAAAABQc3RTYm9vbAEAAAAASW50ZWVudW0AAAAASW50ZQAAAABJbWcgAAAAD3ByaW50U2l4dGVlbkJpdGJvb2wAAAAAC3ByaW50ZXJOYW1lVEVYVAAAAAEAAAAAAA9wcmludFByb29mU2V0dXBPYmpjAAAADABQAHIAbwBvAGYAIABTAGUAdAB1AHAAAAAAAApwcm9vZlNldHVwAAAAAQAAAABCbHRuZW51bQAAAAxidWlsdGluUHJvb2YAAAAJcHJvb2ZDTVlLADhCSU0EOwAAAAACLQAAABAAAAABAAAAAAAScHJpbnRPdXRwdXRPcHRpb25zAAAAFwAAAABDcHRuYm9vbAAAAAAAQ2xicmJvb2wAAAAAAFJnc01ib29sAAAAAABDcm5DYm9vbAAAAAAAQ250Q2Jvb2wAAAAAAExibHNib29sAAAAAABOZ3R2Ym9vbAAAAAAARW1sRGJvb2wAAAAAAEludHJib29sAAAAAABCY2tnT2JqYwAAAAEAAAAAAABSR0JDAAAAAwAAAABSZCAgZG91YkBv4AAAAAAAAAAAAEdybiBkb3ViQG/gAAAAAAAAAAAAQmwgIGRvdWJAb+AAAAAAAAAAAABCcmRUVW50RiNSbHQAAAAAAAAAAAAAAABCbGQgVW50RiNSbHQAAAAAAAAAAAAAAABSc2x0VW50RiNQeGxASQAAAAAAAAAAAAp2ZWN0b3JEYXRhYm9vbAEAAAAAUGdQc2VudW0AAAAAUGdQcwAAAABQZ1BDAAAAAExlZnRVbnRGI1JsdAAAAAAAAAAAAAAAAFRvcCBVbnRGI1JsdAAAAAAAAAAAAAAAAFNjbCBVbnRGI1ByY0BZAAAAAAAAAAAAEGNyb3BXaGVuUHJpbnRpbmdib29sAAAAAA5jcm9wUmVjdEJvdHRvbWxvbmcAAAAAAAAADGNyb3BSZWN0TGVmdGxvbmcAAAAAAAAADWNyb3BSZWN0UmlnaHRsb25nAAAAAAAAAAtjcm9wUmVjdFRvcGxvbmcAAAAAADhCSU0D7QAAAAAAEAAyAAAAAQABADIAAAABAAE4QklNBCYAAAAAAA4AAAAAAAAAAAAAP4AAADhCSU0EDQAAAAAABAAAAFo4QklNBBkAAAAAAAQAAAAeOEJJTQPzAAAAAAAJAAAAAAAAAAABADhCSU0nEAAAAAAACgABAAAAAAAAAAE4QklNA/UAAAAAAEgAL2ZmAAEAbGZmAAYAAAAAAAEAL2ZmAAEAoZmaAAYAAAAAAAEAMgAAAAEAWgAAAAYAAAAAAAEANQAAAAEALQAAAAYAAAAAAAE4QklNA/gAAAAAAHAAAP////////////////////////////8D6AAAAAD/////////////////////////////A+gAAAAA/////////////////////////////wPoAAAAAP////////////////////////////8D6AAAOEJJTQQAAAAAAAACAAE4QklNBAIAAAAAAAQAAAAAOEJJTQQwAAAAAAACAQE4QklNBC0AAAAAAAYAAQAAAAI4QklNBAgAAAAAABAAAAABAAACQAAAAkAAAAAAOEJJTQQeAAAAAAAEAAAAADhCSU0EGgAAAAADSQAAAAYAAAAAAAAAAAAAAMgAAADIAAAACgBVAG4AdABpAHQAbABlAGQALQAyAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAADIAAAAyAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAABAAAAABAAAAAAAAbnVsbAAAAAIAAAAGYm91bmRzT2JqYwAAAAEAAAAAAABSY3QxAAAABAAAAABUb3AgbG9uZwAAAAAAAAAATGVmdGxvbmcAAAAAAAAAAEJ0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YWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDYuMC1jMDAyIDc5LjE2NDQ2MCwgMjAyMC8wNS8xMi0xNjowNDoxNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIxLjIgKFdpbmRvd3MpIiB4bXA6Q3JlYXRlRGF0ZT0iMjAyNC0wNy0wOVQxOTo0MTowNCswNTozMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyNC0wNy0wOVQxOTo0MTowNCswNTozMCIgeG1wOk1vZGlmeURhdGU9IjIwMjQtMDctMDlUMTk6NDE6MDQrMDU6MzAiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6OTQ1OWE1NzEtNjM3MC04ZDQzLTlhMzQtODE1NGY2Y2VkNDg3IiB4bXBNTTpEb2N1bWVudElEPSJhZG9iZTpkb2NpZDpwaG90b3Nob3A6N2M0ODc1ZTAtMTM5ZS1iYjQzLThjYTYtMzA1YjU5ZGUwZTg4IiB4bXBNTTpPcmlnaW5hbERvY3VtZW50SUQ9InhtcC5kaWQ6Mzc4MTc3ODItYzcxOS05YzQ1LWI4MTUtOWQyZDJiYTlkZWRhIiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiBwaG90b3Nob3A6SUNDUHJvZmlsZT0ic1JHQiBJRUM2MTk2Ni0yLjEiIGRjOmZvcm1hdD0iaW1hZ2UvanBlZyI+IDx4bXBNTTpIaXN0b3J5PiA8cmRmOlNlcT4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNyZWF0ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6Mzc4MTc3ODItYzcxOS05YzQ1LWI4MTUtOWQyZDJiYTlkZWRhIiBzdEV2dDp3aGVuPSIyMDI0LTA3LTA5VDE5OjQxOjA0KzA1OjMwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgMjEuMiAoV2luZG93cykiLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjk0NTlhNTcxLTYzNzAtOGQ0My05YTM0LTgxNTRmNmNlZDQ4NyIgc3RFdnQ6d2hlbj0iMjAyNC0wNy0wOVQxOTo0MTowNCswNTozMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIxLjIgKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8cGhvdG9zaG9wOkRvY3VtZW50QW5jZXN0b3JzPiA8cmRmOkJhZz4gPHJkZjpsaT5hZG9iZTpkb2NpZDpwaG90b3Nob3A6OWE2M2MyMmYtZWZhZi1jOTQxLTg5ZTktNTU5Nzc5MTQyZjQ5PC9yZGY6bGk+IDwvcmRmOkJhZz4gPC9waG90b3Nob3A6RG9jdW1lbnRBbmNlc3RvcnM+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg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',
                email_verification_token=verification_token
            )

            company_dict = company_entity.dict(by_alias=True)
            result = await self.__collection.insert_one(company_dict)

            await self.send_verification_email(entity.admin_email, verification_token)

            action_result.data = result.inserted_id
            action_result.message = "Company created successfully. Please verify your email."
        except Exception as e:
            action_result.status = False
            action_result.message = "Failed to create company."
            print(e)
        finally:
            return action_result
    async def delete_company_by_email(self, email: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            delete_result = await self.__collection.delete_one({"admin_email": email})
            if delete_result.deleted_count == 1:
                action_result.message = "Company record deleted successfully."
            else:
                action_result.status = False
                action_result.message = "No company record found with the given email."
        except Exception as e:
            action_result.status = False
            action_result.message = "Failed to delete company record."
            print(e)
        finally:
            return action_result


    async def send_verification_email(self, email: str, verification_token: str):
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'devinsightlemon@gmail.com'
        smtp_password = 'fvgj qctg bvmq zkva'

        verification_url = f"http://127.0.0.1:8000/verify-email?token={verification_token}"

        sender_email = smtp_username
        receiver_email = email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Verify Your Email'

        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #0077be;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #0077be;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Verify Your Email</h1>
                <p>Hello,</p>
                <p>Thank you for signing up. Please click the button below to verify your email address:</p>
                <a href="{verification_url}" class="button">Verify Email</a>
                <p>If the button above doesn't work, you can also copy and paste the following link into your browser:</p>
                <p>{verification_url}</p>
                <p>Thank you,<br>Your Company Team</p>
            </div>
            <div class="footer">
                <p>This email was sent by Your Company. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """

        message.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Verification email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")

    async def check_email_exists(self, email: str) -> bool:
        company = await self.__collection.find_one({"admin_email": email})
        return company is not None
    async def check_email_exists(self, email: str) -> bool:
        try:
            company = await self.__collection.find_one({"admin_email": email})
            if company and not company.get("email_verified", False):
                await self.delete_company_by_email(email)
                return False
            return company is not None
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

    async def check_email(self, email: str) -> bool:
        try:
            result = await self.__collection.find_one({"admin_email": email})
            return result is not None
        except Exception as e:
            print(e)
            return False

    async def get_company_by_admin_email(self, email: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.find_one({"admin_email": email})
            if result:
                json_doc = json.loads(json_util.dumps(result))
                action_result.data = CompanyModel(**json_doc)
                action_result.message = "Company found"
            else:
                action_result.status = False
                action_result.message = "Company not found"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
        finally:
            return action_result
## worked till 2024.06.29
    async def update_company_by_email(self, admin_email: str, update_data: UpdateCompanyModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            update_fields = {}
            if update_data.company_name:
                update_fields["company_name"] = update_data.company_name
            if update_data.company_address:
                update_fields["company_address"] = update_data.company_address
            if update_data.phone_number:
                update_fields["phone_number"] = update_data.phone_number
            if update_data.logo_url:
                update_fields["logo_url"] = update_data.logo_url

            result = await self.__collection.update_one(
                {"admin_email": admin_email},
                {"$set": update_fields}
            )
            if result.modified_count == 1:
                action_result.message = "Update successful"
            else:
                action_result.status = False
                action_result.message = "Update failed or no changes made"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
        finally:
            return action_result

    async def get_members_by_organization_email(self, organization_email: str) -> ActionResult:
        print(organization_email)
        action_result = ActionResult(status=True)

        try:
            query = {"companyEmail": organization_email}
            projection = {"username": 1, "email": 1, "role": 1, "profileStatus": 1, "profilePicture": 1}
            cursor = self.__collection.find(query, projection)

            members = []
            async for document in cursor:
                json_doc = json.loads(json_util.dumps(document))
                members.append(MemberModel(**json_doc))
            action_result.data = members
            action_result.message = "Members retrieved successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
        finally:
            return action_result

    async def block_unblock_member(self, organization_email: str, email: str, action: str) -> ActionResult:
        try:
            query = {"companyEmail": organization_email, "email": email}
            # Determine the new profile status based on the action
            new_status: Optional[str] = None
            if action == 'block':
                new_status = 'Suspend'
            elif action == 'unblock':
                new_status = 'Active'
            else:
                return ActionResult(status=False, message="Invalid action specified")
            # Update the profileStatus in the database
            result = await self.__collection.update_one(query, {"$set": {"profileStatus": new_status}})

            if result.modified_count == 1:
                return ActionResult(status=True, message=f"Member {email} {action}ed successfully1")
            else:
                return ActionResult(status=False, message=f"Failed to {action} member or no changes made1")

        except Exception as e:
            return ActionResult(status=False, message=f"Error occurred: {str(e)}")

    async def get_organizations_with_custom_domain(self) -> ActionResult:
        action_result = ActionResult(status=True)

        try:
            query = {"has_custom_domain": True}
            projection = {"company_name": 1, "admin_email": 1, "domain": 1}
            cursor = self.__collection.find(query, projection)

            organizations = []
            async for document in cursor:
                json_doc = json.loads(json_util.dumps(document))
                organizations.append({
                    "company_name": json_doc["company_name"],
                    "admin_email": json_doc["admin_email"],
                    "domain": json_doc["domain"]
                })
            action_result.data = organizations
            action_result.message = "Organizations with custom domains retrieved successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
        finally:
            return action_result

    async def update_member_role(self, organization_email: str, email: str, new_role: str) -> ActionResult:
        try:
            query = {"companyEmail": organization_email, "email": email}
            result = await self.__collection.update_one(query, {"$set": {"role": new_role}})

            if result.modified_count == 1:
                return ActionResult(status=True, message="Role updated successfully")
            else:
                return ActionResult(status=False, message="Role update failed or no changes made")

        except Exception as e:
            return ActionResult(status=False, message=f"Error occurred: {str(e)}")

    async def send_changerole_email(self, username: str, email: str, new_role: str):
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'devinsightlemon@gmail.com'
        smtp_password = 'fvgj qctg bvmq zkva'


        sender_email = smtp_username
        receiver_email = email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Role changed'

        body = f"""
        Hello,

        Hello {username} Your active role have been change to {new_role}.
        

        Thank you,
        Devinsight Team
        """
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"imforming email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send informing email: {str(e)}")

    async def update_email_verification(self, email: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            result = await self.__collection.update_one(
                {"admin_email": email},
                {"$set": {"email_verified": True}}
            )
            if result.modified_count == 1:
                action_result.message = "Email verified successfully"
            else:
                action_result.status = False
                action_result.message = "Invalid or expired token"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
            action_result.message = str(e)  # Capture the exact error message
            print(f"Error adding review: {e}")
        finally:
            return action_result


    async def get_invitations_by_organization_email(self, organization_email: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            invitations = []
            query = {"organization_email": organization_email, "invite_accepted": False}
            projection = {
                "_id": 1,  # Exclude the _id field
                "user_email": 1,
                "role": 1,
                "sent_date": 1
            }

            cursor = self.__collection.find(query, projection)
            async for document in cursor:
                json_doc = json.loads(json_util.dumps(document))
                invitations.append(json_doc)

            action_result.data = invitations
            action_result.message = "Invitations retrieved successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
            print(e)
        finally:
            return action_result
        
    async def get_organization_name_by_email(self, adminEmail:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            reult = await self.__collection.find_one({"admin_email":adminEmail})
            if reult is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                action_result.data = reult.get("company_name")
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result    
    async def get_organization_image_by_email(self, adminEmail:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            reult = await self.__collection.find_one({"admin_email":adminEmail})
            if reult is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                action_result.data = reult.get("logo_url")
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result     

    async def send_invite(self, invite_data: dict) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            # Generate a verification token
            serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
            verification_token = serializer.dumps({
                "email": invite_data["user_email"],
                "organization_email": invite_data["organization_email"],
                "organization_name": invite_data["organization_name"],
                "role": invite_data["role"]
            }, salt='invitation_salt')

            invite_data['verification_token'] = verification_token
            invite_data['sent_date'] = datetime.utcnow().isoformat()

            # Insert invite data into the database
            result = await self.__collection.insert_one(invite_data)

            # Send verification email
            await self.send_invitation_email(invite_data['user_email'], verification_token)

            action_result.data = str(result.inserted_id)
            action_result.message = "Invite sent successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = "Failed to send invite"
            print(e)
        finally:
            return action_result  


    async def resend_invite(self, invite_id: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            invite = await self.__collection.find_one({"_id": ObjectId(invite_id)})
            if invite:
                user_email = invite["user_email"]
                verification_token = invite["verification_token"]

                # Resend the verification email
                await self.send_verification_email(user_email, verification_token)

                action_result.message = "Invite resent successfully"
            else:
                action_result.status = False
                action_result.message = "Invite not found"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
            print(e)
        finally:
            return action_result


    async def delete_invite(self, invite_id: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            delete_result = await self.__collection.delete_one({"_id": ObjectId(invite_id)})
            if delete_result.deleted_count == 1:
                action_result.message = "Invite deleted successfully"
            else:
                action_result.status = False
                action_result.message = "Invite not found or delete failed"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
            print(e)
        finally:
            return action_result
        
    async def accept_invite(self, email: str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            update_result = await self.__collection.find_one_and_update(
                {"user_email": email},
                {"$set": {"invite_accepted": True}},
                return_document=ReturnDocument.AFTER
            )
            if update_result:
                action_result.message = "Invite accepted successfully"
            else:
                action_result.status = False
                action_result.message = "Invite not found or update failed"
        except Exception as e:
            action_result.status = False
            action_result.message = f"Error occurred: {str(e)}"
            print(e)
        finally:
            return action_result

    async def send_invitation_email(self, email: str, verification_token: str):
        # This method is for sending email verification, adjust it as per resend logic if needed
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'devinsightlemon@gmail.com'
        smtp_password = 'fvgj qctg bvmq zkva'

        
        verification_url = f"http://localhost:5173/SignUpInvite?token={verification_token}&email={email}"

        sender_email = smtp_username
        receiver_email = email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = 'Verify Your Email'

        body = f"""
        Hello,

        Please click the following link to verify your email:
        {verification_url}

        Thank you,
        Your Company Team
        """
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Verification email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")
        finally:
            return 0

    async def add_request(self, entity: BaseModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            get_next_request_id_pipeline = [
                {
                    "$match": {
                        "user": entity.user,
                        "p_id": entity.p_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "next_request_id": {"$max": "$r_id"}
                    }
                },
                {
                    "$project": {
                        "next_request_id": {
                            "$ifNull": [
                                {"$add": ["$next_request_id", 1]},
                                1
                            ]
                        }
                    }
                }
            ]

            next_id_cursor = self.__collection.aggregate(get_next_request_id_pipeline)
            next_id_doc = await next_id_cursor.to_list(length=1)
            next_request_id = next_id_doc[0]['next_request_id'] if next_id_doc else 1

            entity_dict = entity.dict(by_alias=True, exclude={"id"})
            entity_dict['r_id'] = next_request_id

            result = await self.__collection.insert_one(entity_dict)
            action_result.data = str(result.inserted_id)
            action_result.message = "Insert successful"
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)
        finally:
            return action_result

    async def get_latest_r_id(self, user: str, p_id: Optional[str] = None) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            query = {"user": user}
            if p_id is not None:
                query["p_id"] = p_id

            # Assuming your collection has a field indicating insertion order or using the default _id
            latest_entity = await self.__collection.find_one(query, sort=[("r_id", DESCENDING)])
            if latest_entity is None:
                action_result.message = TextMessages.NOT_FOUND
                action_result.status = False
            else:
                action_result.data = latest_entity.get("r_id")
                action_result.message = TextMessages.FOUND
        except Exception as e:
            action_result.status = False
            action_result.message = TextMessages.ACTION_FAILED
        finally:
            return action_result


    async def add_response(self, entity: BaseModel) -> ActionResult:
            action_result = ActionResult(status=True)
            try:
                entity_dict = entity.dict(by_alias=True, exclude={"id"})
                result = await self.__collection.insert_one(entity_dict)
                action_result.data = str(result.inserted_id)
                action_result.message = "Insert successful"
            except Exception as e:
                action_result.status = False
                action_result.message = str(e)
            finally:
                return action_result

    async def delete_request(self, p_id: int, user: str, r_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            document = await self.__collection.find_one({"p_id": p_id, "user": user, "r_id": r_id})
            if document:
                delete_result = await self.__collection.delete_one({"p_id": p_id, "user": user, "r_id": r_id})
                if delete_result.deleted_count == 1:
                    document["deleted_at"] = datetime.utcnow()  # Add deletion timestamp
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
            print(f"Error deleting request: {e}")
        finally:
            return action_result

    async def get_all_requests(self, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({"user": user}):
                if 'p_id' in document and document['p_id'] is not None:
                    json_doc = json.loads(json_util.dumps(document))
                    try:
                        documents.append(RequestItem(**json_doc))
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

    async def get_request_by_id(self, entity_id: int, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": entity_id, "user": user})
            if entity is None:
                action_result.message = "Not found"
                action_result.status = False
            else:
                json_data = json.loads(json_util.dumps(entity))
                action_result.data = json_data
                action_result.message = "Found"
        except Exception as e:
            action_result.status = False
            action_result.message = "Action failed"
        finally:
            return action_result


    async def get_request_by_id_and_user(self, entity_id: int, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({"p_id": entity_id, "user":user}):
                if 'p_id' in document and document['p_id'] is not None:
                    json_doc = json.loads(json_util.dumps(document))
                    try:
                        documents.append(RequestItem(**json_doc))
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


    async def get_response_by_id_and_user(self, entity_id: int, user:str) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            documents = []
            async for document in self.__collection.find({"p_id": entity_id, "user":user}):
                if 'p_id' in document and document['p_id'] is not None:
                    json_doc = json.loads(json_util.dumps(document))
                    try:
                        documents.append(ResponseItem(**json_doc))
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

    async def get_response_by_id(self, p_id: int, user:str, r_id) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"p_id": p_id, "user":user, 'r_id':r_id})
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

    async def get_requests_by_qae(self, qae: str) -> List[RequestItem]:
        requests_cursor = self.__collection.find({"qae": qae})
        requests = await requests_cursor.to_list(length=None)
        return [RequestItem(**request) for request in requests]

    async def get_responses_by_criteria(self, user: str, p_id: int, r_id: int) -> List[ResponseItem]:
        responses_cursor = self.__collection.find({'user': user, 'p_id': p_id, 'r_id': r_id})
        responses = await responses_cursor.to_list(length=None)
        return [ResponseItem(**response) for response in responses]

    async def get_user_by_email(self, email: str):
        from utilis.profile import serialize_dict
        entity = await self.__collection.find_one({"email": email})
        if entity:
            entity = serialize_dict(entity)
        return entity

    async def get_organization_by_email(self, email: str):
        from utilis.profile import serialize_dict
        entity = await self.__collection.find_one({"admin_email": email})
        if entity:
            entity = serialize_dict(entity)
        return entity

    async def add_user_profile(self, entity: BaseModel):
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})
        await self.__collection.insert_one(entity_dict)
    async def add_user_skills(self, entity: BaseModel):
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})
        await self.__collection.insert_one(entity_dict)
    

    async def authenticate_user(self, email: str, password: str):
        from utilis.profile import verify_password
        existing_user = await self.__collection.find_one({"email": email})
        if not existing_user or not verify_password(password, existing_user["password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        return existing_user

    async def update_user_status(self, entity: BaseModel):
        await self.__collection.update_one(
                {"email": entity.email},
                {"$set": {"profileStatus": "Active"}}
            )

    async def deactivate_users(self, email: str):
        user = await self.__collection.find_one({"email": email, "profileStatus": {"$ne": "Suspend"}})
        if user:
            await self.__collection.update_one({"email": email}, {"$set": {"profileStatus": "Suspend"}})
            return {"message": "Account deactivated successfully"}
        raise HTTPException(status_code=404, detail="User not found or account already deactivated")

    async def delete_user_profile(self, email: str):
        result=await self.__collection.delete_one({"email": email})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}

    async def save_user_profile(self, email: str, profile_data: dict):
        await self.__collection.update_one(
            {"email": email},
            {"$set": profile_data},
            upsert=True
        )
    async def save_user_skills(self, email: str, skills_data: dict):
        await self.__collection.update_one(
            {"email": email},
            {"$set": skills_data},
            upsert=True
        )

    async def get_user_profile_by_id(self, email: str):
        user = await self.__collection.find_one({"email": email}, {"_id": 0})
        return user

    async def update_password(self, email: str, password: str):
        await self.__collection.update_one({"email": email}, {"$set": {"password": password}})
    
    async def update_password_organizaiton(self, email: str, password: str):
        await self.__collection.update_one({"admin_email": email}, {"$set": {"hash_password": password}})

    async def save_verification_code(self, entity: BaseModel):
        await self.__collection.update_one(
        {"email": entity.email},
        {"$set": {"verificationCode": entity.verificationCode}},upsert=True
        )
        return {"message": "Verification code saved"}

    async def get_verify_code(self, entity: BaseModel):
        return await self.__collection.get(entity.email)

    async def update_profile_status(self, entity: BaseModel):
        result =await self.__collection.update_one(
            {"email": entity.email},
            {"$set": {"profileStatus": entity.profileStatus}}
            )
        return result

    async def update_register_face(self, email: str, face_data: dict):
        await self.__collection.update_one({"email": email}, {"$set": face_data})

    async def login_face(self):
        return await self.__collection.find().to_list(length=None)

    async def update_feedback(self, feedback_request: SendFeedback) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            query = {"p_id": feedback_request.p_id, "r_id": feedback_request.r_id, "user": feedback_request.user}
            update = {"$set": {"feedback": feedback_request.feedback}}
            result = await self.__collection.update_one(query, update)

            if result.matched_count == 0:
                action_result.status = False
                action_result.message = "Request not found"
            else:
                action_result.message = "Feedback submitted successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)

        return action_result

    async def update_qae(self, assign_request: AssignItem) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            query = {"p_id": assign_request.p_id, "r_id": assign_request.r_id, "user": assign_request.user}
            update = {"$set": {"qae": assign_request.qae}}
            result = await self.__collection.update_one(query, update)

            if result.matched_count == 0:
                action_result.status = False
                action_result.message = "Request not found"
            else:
                action_result.message = "Feedback submitted successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)

        return action_result

    async def update_forwardqae(self, assign_forward: AssignForwardItem) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            query = {"p_id": assign_forward.p_id, "r_id": assign_forward.r_id, "user": assign_forward.user}
            update = {"$set": {"qae": assign_forward.selectedName}}
            result = await self.__collection.update_one(query, update)

            if result.matched_count == 0:
                action_result.status = False
                action_result.message = "Request not found"
            else:
                action_result.message = "Feedback submitted successfully"
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)

        return action_result

    async def update_response(self, response_request: UpdateResponseRequest) -> ActionResult:
        action_result = ActionResult(status=True, message="")

        try:
            query = {
                "p_id": response_request.p_id,
                "r_id": response_request.r_id,
                "user": response_request.user
            }
            update = {
                "$set": {
                    "response_content": response_request.response_content,
                    "response_status": "Responded",
                    "date": datetime.now().strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
                }
            }
            result: UpdateResult = await self.__collection.update_one(query, update)

            if result.matched_count == 0:
                action_result.status = False
                action_result.message = "Response not found"
            else:
                action_result.message = "Response updated successfully"

        except Exception as e:
            action_result.status = False
            action_result.message = str(e)

        return action_result

    async def update_request_status(self, request_status: UpdateRequestStatus) -> ActionResult:
        action_result = ActionResult(status=True, message="")

        try:
            query = {
                "p_id": request_status.p_id,
                "r_id": request_status.r_id,
                "user": request_status.user
            }
            update = {
                "$set": {
                    "r_status": request_status.r_status
                }
            }
            result: UpdateResult = await self.__collection.update_one(query, update)

            if result.matched_count == 0:
                action_result.status = False
                action_result.message = "Request not found"
            else:
                action_result.message = "Request status updated to Completed"

        except Exception as e:
            action_result.status = False
            action_result.message = str(e)

        return action_result

