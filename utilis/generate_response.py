import logging
from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
import os
# from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from config import config

class CodeReviewLLM:

    @staticmethod
    def get_review(chunk_input, language1, description1):
        try:
            # Set the Google API key
            os.environ['GOOGLE_API_KEY'] = config.Configurations.google_api_key
            if not config.Configurations.google_api_key:
                raise ValueError("Missing GOOGLE_API_KEY environment variable")

            # Initialize the model
            model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

            # Define the prompt templates
            prompt1 = PromptTemplate(
                input_variables=['con'],
                template="This is a code written by a programmer {con}, and I need you to review this code. Give Syntax errors, Semantic Errors, and give a good review considering the code."
            )

            # Initialize the output parser
            output_parser = StrOutputParser()

            # Define the chains
            chain1 = prompt1 | model | output_parser

            # Set the main language
            main_language = language1

            # Initialize the previous answer
            previous_answer = ""

            # Define the chunking process
            def create_cohesive_prompt(current_chunk, lan, des):
                prompt = f"This is a code written by a programmer in the language of {lan}, it is for a project on {des}. Use this code {current_chunk} and review this code. Give Syntax errors, Semantic Errors, and give a good review considering the code line by line number and mention code line also, when you explaining something,Be precise and concise"
                return prompt

            # Initialize the compilation
            comp = "This is the review: \n"

            # Process each chunk
            for chunk in chunk_input:
                project_nature = description1
                cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_nature)
                r = chain1.invoke({"con": cohesive_prompt})
                comp = comp + r
                previous_answer = r

            # Print the final output
            return comp

        except Exception as e:
            logging.error(f"Error in generating review content: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    @staticmethod
    def get_suggestions(chunk_input, review):
        try:
            # Set the Google API key
            os.environ['GOOGLE_API_KEY'] = config.Configurations.google_api_key
            if not config.Configurations.google_api_key:
                raise ValueError("Missing GOOGLE_API_KEY environment variable")

            # Initialize the model
            model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

            # Define the prompt templates
            prompt2 = PromptTemplate(
                input_variables=['con'],
                template="This is a code written by a programmer {con}. I asked for a review from your services. Now I need to give suggestions for Develop Programming Skills, Build Confidence, Enhance Problem-Solving Abilities, Create Reliable Software, Improve Efficiency, Facilitate Collaboration, Learn Best Practices, Ensure Security, Prepare for Professional Work, Reduce Debugging Time."
            )

            # Initialize the output parser
            output_parser = StrOutputParser()

            # Define the chains
            chain1 = prompt2 | model | output_parser

            # Set the main language
            rev = review

            # Initialize the previous answer
            previous_answer = ""

            # Define the chunking process
            def create_cohesive_prompt2(current_chunk):
                prompt = f"This is a code written by a programmer {current_chunk}. Using this code {current_chunk} I asked for a review from your services, and this is it: {rev}. Using the code and review, Give suggestions considering code snippet that you have identify this part can improve. Give all the suggestions that you have identified. Also mentioned that code snippet with suggestion."
                return prompt

            # Initialize the compilation
            comp = "Suggestions : \n"

            # Process each chunk
            for chunk in chunk_input:
                cohesive_prompt = create_cohesive_prompt2(chunk)
                r = chain1.invoke({"con": cohesive_prompt})
                comp = comp + r
                previous_answer = r

            # Print the final output
            return comp

        except Exception as e:
            logging.error(f"Error in generating review content: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")