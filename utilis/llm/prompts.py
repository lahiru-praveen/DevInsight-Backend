from langchain.prompts import PromptTemplate

def create_cohesive_prompt(current_chunk, lan, des):
    prompt = f"This is a code written by a programmer in the language of {lan}, also this is the description given by programmer {des}. Use this code {current_chunk} and review this code.Be precise and concise"
    return prompt

# Define the prompt templates
prompt1 = PromptTemplate(
    input_variables=['con','review_template'],
    template="This is a code written by a programmer, Details : {con}. I need you to review this code. Generate a code review using this given template for the code review {review_template}. "
)

prompt2 = PromptTemplate(
    input_variables=['con','review',],
    template="There is a code written by programmer, For additional details: {con}. I asked for a review from your services. This is the review I got from your service {review}. Now I need to get the suggestions. My want suggestions for Develop Programming Skills, Build Confidence, Enhance Problem-Solving Abilities, Create Reliable Software, Improve Efficiency, Facilitate Collaboration, Learn Best Practices, Ensure Security, Prepare for Professional Work, Reduce Debugging Time. Give me the suggestion that you have identified in the code segment. use the review also. dont repeat the same thing mentioned by in the review. and give the suggestions using the code snippets. "
)

prompt3 = PromptTemplate(
    input_variables=['con','review','suggestion'],
    template="There is a code written by programmer, For additional details: {con}. I asked for a review from your services. This is the review I got from your service {review}. Then i asked suggestion from your service and this is the what i got {suggestion}. Now what I need is I need Reference links to send to the programmer for refer and learn. When you suggest refer links consider the review and suggestions. Because using suggestions and review identify what areas programmer should have to learn and refer. Give these kind of web site links that you have identify as programmer should have to learn those areas in that relevant programming Language."
)