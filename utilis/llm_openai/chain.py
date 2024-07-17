import openai
from config import config
from utilis.llm_openai.prompt import prompt1, prompt2, prompt3

# Set OpenAI API key
openai.api_key = config.Configurations.openai_api_key

# Define a function to call OpenAI API
def call_openai_model(prompt, temperature=0.5):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content

# Define the chains
def chain1(con, review_template):
    prompt = prompt1.format(con=con, review_template=review_template)
    return call_openai_model(prompt)

def chain2(con, review):
    prompt = prompt2.format(con=con, review=review)
    return call_openai_model(prompt)

def chain3(con, review, suggestion):
    prompt = prompt3.format(con=con, review=review, suggestion=suggestion)
    return call_openai_model(prompt)