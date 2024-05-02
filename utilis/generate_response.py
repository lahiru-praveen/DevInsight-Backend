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
    def test_llm(chunk_input, language1, description1):
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
                template="This is a code written by a programmer {con}, and I need you to review this code. Give strengths and weaknesses and potential modifications,Be precise and concise "
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
            def create_cohesive_prompt(current_chunk, main_language, project_nature):
                prompt = f"This is a code written by a programmer in the language of {main_language}, it is for a project on {project_nature}. Use this code {current_chunk} and review this code. Give strengths and weaknesses and potential modifications,Be precise and concise"
                return prompt

            # Initialize the compilation
            comp = "This is the review: \n"

            # Process each chunk
            for chunk in chunk_input:
                project_nature = description1
                cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_nature)
                # try:
                r = chain1.invoke({"con": cohesive_prompt})
                # except (ChatGoogleGenerativeAIError, HTTPException) as e:
                #     logging.error(f"Error in generating review content: {e}")
                #     raise HTTPException(status_code=500, detail="Internal Server Error")
                comp = comp + r
                previous_answer = r

            # Print the final output
            return comp

        except Exception as e:
            logging.error(f"Error in generating review content: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")