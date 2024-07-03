from utilis.llm.chain import chain1,chain2,chain3
from utilis.llm.prompts import create_cohesive_prompt


class CodeReviewLLM:
    @staticmethod
    def get_review(chunk_input, language1, description1):
        # Set the main language
        main_language = language1

        # Set the Description
        project_description = description1

        # Define a review template
        review_template = "1. **Accuracy**:\n\t- Does the code meet the feature requirements? (Yes/No)\n\t- Missing functionality or poorly implemented functions: [Details]\n\t- Suggested related functions that could be added: [Details]\n2. **Error Handling**:\n\t- How well does the code manage errors? (Good/Fair/Poor)\n\t- Potential exceptions or edge cases not handled: [Details]\n3. **Readability**:\n\t- Is the code easy to read and understand? (Yes/No)\n\t- Best practices for clarity and brevity followed: (Yes/No)\n\t- Clarity of function, method, or class roles: (Clear/Unclear)\n\t- Code broken into easy-to-understand chunks: (Yes/No)\n4. **Maintainability**:\n\t- Ease of maintaining and adjusting the code in the future: (Easy/Moderate/Difficult)\n\t- Ease of testing and debugging: (Easy/Moderate/Difficult)\n\t- Avoidance of outdated dependencies or tightly coupled components: (Yes/No)\n5. **Performance**:\n\t- Performance issues identified: [Details]\n\t- Impact on overall system performance: [Details]\n6. **Security**:\n\t- Security vulnerabilities found: [Details]\n\t- Proper handling of user data and inputs: (Yes/No)\n7. **Documentation**:\n\t- Adequate documentation explaining the code’s purpose and usage: (Yes/No)\n\t- Areas needing more documentation: [Details]\n8. **Naming Conventions**:\n\t- Clear and consistent variable, function, and class names: (Yes/No)\n\t- Recommendations for naming improvements: [Details]\n**Overall Assessment**:\n\t- General assessment of the code quality: [Details]\n\t- Final verdict (Approve / Approve with Changes / Request Changes / Hold / Other): [Decision]\n**Next Steps**:\n\t- Recommended next steps or actions based on the review decision: [Details]\n**Additional Comments**:\n\t- [Add any additional comments or suggestions not covered in the above sections.]"

        # Initialize the previous answer
        previous_answer = ""

        # Initialize the compilation
        review_final = "This is the review: \n"

        # Process each chunk
        for chunk in chunk_input:
            cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_description)
            response = chain1.invoke({"con": cohesive_prompt, "review_template": review_template})
            review_final = review_final + response
            previous_answer = response

        review = review_final

        # Initialize the compilation
        suggest_final = "These are the suggestions: \n"

        for chunk in chunk_input:
            cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_description)
            response = chain2.invoke({'con': cohesive_prompt, 'review': review})
            suggest_final = suggest_final + response
            previous_answer = response

        suggestions = suggest_final

        refer_links_final = "These are the Reference Links: \n"

        for chunk in chunk_input:
            cohesive_prompt = create_cohesive_prompt(chunk, main_language, project_description)
            response = chain3.invoke({'con': cohesive_prompt, 'review': review, "suggestion": suggestions})
            refer_links_final = refer_links_final + response
            previous_answer = response

        refer_link = refer_links_final

        return review,suggestions,refer_link








