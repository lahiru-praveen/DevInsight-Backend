from langchain.prompts import PromptTemplate

def create_cohesive_prompt(current_chunk, lan, des):
    prompt = f"This is a code written by a programmer in the language of {lan}, also this is the description given by programmer {des}. Use this code {current_chunk} and review this code. Be precise and concise, and thorough in your review."
    return prompt

# Define the prompt templates
prompt1 = PromptTemplate(
    input_variables=['con', 'review_template'],
    template="This is a code written by a programmer. Details: {con}. Review this code using the given template. Ensure that your review covers all aspects mentioned in the template and provides detailed feedback. {review_template}"
)

prompt2 = PromptTemplate(
    input_variables=['con', 'review'],
    template="Here is a code written by a programmer. For additional details: {con}. A review has been generated: {review}. Provide suggestions that will help in the following areas: Develop Programming Skills, Identify areas where the code can be optimized or improved for better performance, Suggest improvements for better error handling and edge case management, Recommend changes to improve readability and maintainability, Point out any security enhancements that should be made, Advise on best practices for documentation and naming conventions. Use the review to inform your suggestions, and provide code snippets where applicable. Avoid repeating points from the review."
)

prompt3 = PromptTemplate(
    input_variables=['con', 'review', 'suggestion'],
    template="Here is a code written by a programmer. For additional details: {con}. A review has been generated: {review}. Suggestions have been provided: {suggestion}. Now, identify the key areas or concepts used in the code. Provide a list of reference links for further learning and advanced study in these areas, Identify important programming concepts, frameworks, or libraries used in the code, Find high-quality reference links, such as official documentation, tutorials, or advanced guides, that the user can refer to for learning more about these concepts."
)