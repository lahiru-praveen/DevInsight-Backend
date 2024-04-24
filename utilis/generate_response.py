from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate

import os


class TestLLM:
    def test_llm(input_chunks):
        # Set the Google API key
        os.environ['GOOGLE_API_KEY'] = "AIzaSyADYGqAkCJbjwn6Fsnbk5rQHISyRTuFDIE"

        # Initialize the model
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

        # Define the prompt templates
        prompt1 = PromptTemplate(
            input_variables=['con', 'language'],
            template="This is a code written by a programmer {con}, This is written using {language}, and I need you to review this code. Give strengths and weaknesses and potential modifications,Be precise and concise "
        )

        # Initialize the output parser
        output_parser = StrOutputParser()

        # Define the chains
        chain1 = prompt1 | model | output_parser

        # Set the main language
        main_language = "python"

        # Initialize the previous answer
        previous_answer = ""

        # Define the chunking process
        def create_cohesive_prompt(current_chunk, main_language, project_nature):
            prompt = f"This is a code written by a programmer in the language of {main_language}, it is for a project on {project_nature}. Use this code {current_chunk} and review this code. Give strengths and weaknesses and potential modifications,Be precise and concise"
            return prompt

        # Define the topic identification function
        def extract_program_nature(chunk):
            # program extraction logic ek implement karanna
            return "calculator"  # hari eka return krnn. me dummy value hode

        # Initialize the compilation
        comp = "This is the review: \n"

        # Process each chunk
        for chunk in input_chunks:
            project_nature = extract_program_nature(chunk)
            cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_nature)
            r = chain1.invoke({"con": cohesive_prompt, "language": "python"})
            comp = comp + r
            previous_answer = r

        # Generate the final output
        # final = chain2.invoke({"comp": comp, "domain": "artificial intelligence"})

        # Print the final output
        return comp

# Sample usage
# input_chunks = ["def add(a, b):\n    return a + b", "def subtract(a, b):\n    return a - b"]
# print(TestLLM.test_llm(input_chunks))
