import os

# from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
# from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Set Google API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyADYGqAkCJbjwn6Fsnbk5rQHISyRTuFDIE"

# Initialize model
model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# Define prompt template (including input_variables)

yes = True

while (yes):
    prompt = PromptTemplate(
        template=input("User:"),  # Replace with your desired prompt
        input_variables=[]  # Even if you don't have input variables, provide an empty list
    )

    # Initialize output parser
    output_parser = StrOutputParser()

    # Create chain
    chain = prompt | model | output_parser

    # Send prompt and get response
    response = chain.invoke({})

    # Print response
    print("Chatbot:" + response)

    if prompt.template == "No anything":
        yes = False
