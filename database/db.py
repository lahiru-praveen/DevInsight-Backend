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
from models.updatecompany_data import UpdateCompanyModel

##new
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

    # new 
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
        finally:
            return action_result        

    async def check_email_exists(self, email: str) -> bool:
        company = await self.__collection.find_one({"admin_email": email})
        return company is not None
    
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
        
    async def update_company_by_email(self, admin_email: str, update_data: UpdateCompanyModel) -> ActionResult:
        action_result = ActionResult(status=True)
        try:
            update_fields = {
                "company_name": update_data.company_name,
                "company_address": update_data.company_address,
                "phone_number": update_data.phone_number,
                "logo_url": update_data.logo_url  # Ensure this line is included
            }
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
        
    # async def send_verification_email(self, email: str, verification_token: str):
    #     smtp_server = 'smtp.gmail.com'
    #     smtp_port = 587
    #     smtp_username = 'devinsightlemon@gmail.com'
    #     smtp_password = 'fvgj qctg bvmq zkva'

    #     verification_url = f"http://127.0.0.1:8000/verify-email?token={verification_token}&email={email}"

    #     sender_email = smtp_username
    #     receiver_email = email
    #     message = MIMEMultipart()
    #     message['From'] = sender_email
    #     message['To'] = receiver_email
    #     message['Subject'] = 'Verify Your Email'

    #     body = f"""
    #     Hello,

    #     Please click the following link to verify your email:
    #     {verification_url}

    #     Thank you,
    #     Your Company Team
    #     """
    #     message.attach(MIMEText(body, 'plain'))

    #     try:
    #         with smtplib.SMTP(smtp_server, smtp_port) as server:
    #             server.starttls()
    #             server.login(smtp_username, smtp_password)
    #             server.sendmail(sender_email, receiver_email, message.as_string())
    #         print(f"Verification email sent to {receiver_email}")
    #     except Exception as e:
    #         print(f"Failed to send verification email: {str(e)}")

    # async def save_company_data(self, entity: CreateCompanyModel) -> ActionResult:
    #     action_result = ActionResult(status=True)
    #     try:
    #         pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    #         hashed_password = pwd_context.hash(entity.password)

    #         company_entity = CompanyModel(
    #             company_name=entity.company_name,
    #             admin_email=entity.admin_email,
    #             company_address=entity.company_address,
    #             phone_number=entity.phone_number,
    #             has_custom_domain=entity.has_custom_domain,
    #             domain=entity.domain,
    #             hash_password=hashed_password,
    #             email_verified=True,
    #             logo_url=entity.logo_url
    #         )

    #         company_dict = company_entity.dict(by_alias=True)
    #         result = await self.__collection.insert_one(company_dict)

    #         action_result.data = result.inserted_id
    #         action_result.message = "Company data saved successfully."
    #     except Exception as e:
    #         action_result.status = False
    #         action_result.message = "Failed to save company data."
    #         print(e)
    #     finally:
    #         return action_result

    # async def update_email_verification(self, email: str) -> ActionResult:
    #     action_result = ActionResult(status=True)
    #     try:
    #         result = await self.__collection.update_one(
    #             {"admin_email": email},
    #             {"$set": {"email_verified": True}}
    #         )
    #         if result.modified_count == 0:
    #             action_result.status = False
    #             action_result.message = "Email verification failed."
    #         else:
    #             action_result.message = "Email verified successfully."
    #     except Exception as e:
    #         action_result.status = False
    #         action_result.message = f"Failed to update email verification: {str(e)}"
    #         print(e)
    #     finally:
    #         return action_result
    # async def create_company(self, entity: CreateCompanyModel) -> ActionResult:
    #     action_result = ActionResult(status=True)
    #     try:
    #         pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    #         hashed_password = pwd_context.hash(entity.password)

    #         company_entity = CompanyModel(
    #             company_name=entity.company_name,
              
    #             admin_email=entity.admin_email,
    #             company_address=entity.company_address,
    #             phone_number=entity.phone_number,
    #             has_custom_domain=entity.has_custom_domain,
    #             domain=entity.domain,
               
    #             hash_password=hashed_password,
    #             email_verified=False
    #         )

    #         company_dict = company_entity.dict(by_alias=True)
    #         result = await self.__collection.insert_one(company_dict)

    #         action_result.data = result.inserted_id
    #         action_result.message = "Insert successful"
    #     except Exception as e:
    #         action_result.status = False
    #         action_result.message = "Action failed"
    #     finally:
    #         return action_result
    ##   old
        
       

    
    # Add the check_username method
    # async def check_username(self, username: str) -> bool:
    #     try:
    #         result = await self.__collection.find_one({"company_uname": username})
    #         return result is not None
    #     except Exception as e:
    #         print(e)
    #         return False
        

    # def send_verification_email(self, email: str, token: str):
    #     verification_link = f"http://127.0.0.1:8000/verify-email?token={token}"
    #     msg = MIMEText(f"Please verify your email by clicking the following link: {verification_link}")
    #     msg['Subject'] = 'Email Verification'
    #     msg['From'] = 'no-reply@yourdomain.com'
    #     msg['To'] = email

    #     with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #         server.starttls()
    #         server.login('devinsightlemon@gmail.com', 'pnml qaak jdsa xphz')
    #         server.sendmail(msg['From'], [msg['To']], msg.as_string())

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


    # async def get_company_by_token(self, token: str):
    #     try:
    #         result = await self.__collection.find_one({"verification_token": token})
    #         return result
    #     except Exception as e:
    #         print(e)
    #         return None

    # async def verify_company_email(self, company_id: str):
    #     try:
    #         result = await self.__collection.update_one(
    #             {"_id": ObjectId(company_id)},
    #             {"$set": {"email_verified": True, "verification_token": None, "token_expiration": None}}
    #         )
    #         return result.modified_count > 0
    #     except Exception as e:
    #         print(e)
    #         return False
    
    
    # async def update_company_by_email(self, admin_email: str, update_data: UpdateCompanyModel) -> ActionResult:
    #     action_result = ActionResult(status=True)
    #     try:
    #         update_fields = {
    #             "company_name": update_data.company_name,
    #             "company_address": update_data.company_address,
    #             "phone_number": update_data.phone_number
    #         }
    #         result = await self.__collection.update_one(
    #             {"admin_email": admin_email},
    #             {"$set": update_fields}
    #         )
    #         if result.modified_count == 1:
    #             action_result.message = "Update successful"
    #         else:
    #             action_result.status = False
    #             action_result.message = "Update failed or no changes made"
    #     except Exception as e:
    #         action_result.status = False
    #         action_result.message = f"Error occurred: {str(e)}"
    #     finally:
    #         return action_result
    