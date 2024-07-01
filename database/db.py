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
from models.updatecompany_data import UpdateCompanyModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
import secrets
from datetime import datetime

SECURITY_PASSWORD_SALT = secrets.token_hex(16)

class MemberModel(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: str

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
            serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
            verification_token = serializer.dumps(entity.admin_email, salt='email-confirm-salt')

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
                email_verified=False,
                logo_url=entity.logo_url,
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

    # async def check_email_exists(self, email: str) -> bool:
    #     company = await self.__collection.find_one({"admin_email": email})
    #     return company is not None
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
        action_result = ActionResult(status=True)

        try:
            query = {"organization_email": organization_email}
            projection = {"first_name": 1, "last_name": 1, "email": 1, "role": 1}
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
            query = {"organization_email": organization_email, "email": email}
            result = await self.__collection.update_one(query, {"$set": {"role": new_role}})

            if result.modified_count == 1:
                return ActionResult(status=True, message="Role updated successfully")
            else:
                return ActionResult(status=False, message="Role update failed or no changes made")

        except Exception as e:
            return ActionResult(status=False, message=f"Error occurred: {str(e)}")

    async def send_changerole_email(self, first_name: str, last_name: str, email: str, new_role: str):
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

        Hello {first_name} {last_name} Your active role have been change to {new_role}.
        

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


# invitation
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

    async def send_invite(self, invite_data: dict) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            # Generate a verification token
            serializer = URLSafeTimedSerializer(config.Configurations.secret_key)
            verification_token = serializer.dumps({
                "email": invite_data["user_email"],
                "organization_email": invite_data["organization_email"],
                "role": invite_data["role"]
            }, salt=SECURITY_PASSWORD_SALT)

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

    async def send_invitation_email(self, email: str, verification_token: str):
        # This method is for sending email verification, adjust it as per resend logic if needed
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

#     async def add_request(self, entity: BaseModel) -> ActionResult:
#         action_result = ActionResult(status=True)
#         try:
#             get_next_request_id_pipeline = [
#                 {
#                     "$group": {
#                         "_id": None,
#                         "next_request_id": {"$max": "$request_id"}
#                     }
#                 },
#                 {
#                     "$project": {
#                         "next_request_id": {"$ifNull": [{"$add": ["$next_request_id", 1]}, 1]}
#                     }
#                 }
#             ]
#             next_id_cursor = self.__collection.aggregate(get_next_request_id_pipeline)
#             next_id_doc = await next_id_cursor.to_list(length=1)
#             next_request_id = next_id_doc[0]['next_request_id'] if next_id_doc else 1
#
#             entity_dict = entity.dict(by_alias=True, exclude={"id"})
#             entity_dict['request_id'] = next_request_id
#
#             result = await self.__collection.insert_one(entity_dict)
#             action_result.data = str(result.inserted_id)
#             action_result.message = TextMessages.INSERT_SUCCESS
#         except Exception as e:
#             action_result.status = False
#             action_result.message = str(e)
#         finally:
#             return action_result
#
#     async def get_request_by_id(self, entity_id: int) -> ActionResult:
#         action_result = ActionResult(status=True)
#         try:
#             entity = await self.__collection.find_one({"p_id": entity_id})
#             if entity is None:
#                 action_result.message = TextMessages.NOT_FOUND
#                 action_result.status = False
#             else:
#                 json_data = json.loads(json_util.dumps(entity))
#                 action_result.data = json_data
#                 action_result.message = TextMessages.FOUND
#         except Exception as e:
#             action_result.status = False
#             action_result.message = TextMessages.ACTION_FAILED
#         finally:
#             return action_result

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
            action_result.message = "Insert successful"
        except Exception as e:
            action_result.status = False
            action_result.message = str(e)
        finally:
            return action_result

    async def get_request_by_id(self, entity_id: int) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            entity = await self.__collection.find_one({"request_id": entity_id})
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
