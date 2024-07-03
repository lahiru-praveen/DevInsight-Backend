from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
import os
from config import config
from utilis.llm_gemini.prompts import prompt1, prompt2, prompt3

os.environ['GOOGLE_API_KEY'] = config.Configurations.google_api_key

# Initialize the model
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)

# Initialize the output parser
output_parser = StrOutputParser()

# Define the chains
chain1 = prompt1 | model | output_parser
chain2 = prompt2 | model | output_parser
chain3 = prompt3 | model | output_parser

