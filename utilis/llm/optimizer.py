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
        review_template = "\n1. Design:\n            Does the design of the changes make sense in the context of the application?\n            [Provide comments and suggestions related to the design of the changes.]\n2. Functionality:\n            Does the code implement the intended functionality correctly?\n            [Evaluate the functionality and provide feedback on its correctness and user experience.]\n3. Complexity:           \n            Is the code more complex than necessary?\n            [Assess the complexity of the code and suggest simplifications if applicable.]\n4. Tests:            \n            Are appropriate tests included for the changes?\n            [Review the test coverage and suggest additions or improvements if needed.]\n5. Naming and Comments:           \n            Are variable/function names clear and descriptive?\n            [Check the clarity of naming conventions and suggest improvements.]\n            Are comments clear and useful?\n            [Assess the quality of comments and suggest enhancements or clarifications.]\n6. Style and Consistency:           \n            Does the code adhere to coding style guidelines?\n            [Ensure consistency with coding style and provide feedback on any deviations.]\n            Is the code consistent with existing codebase standards?\n            [Check for consistency with existing codebase practices and recommend adjustments if necessary.]\n7. Documentation:            \n            Is documentation updated or added where necessary?\n            [Ensure that relevant documentation is updated to reflect the changes made.]\n8. Review Every Line:          \n            Have all lines of code been reviewed thoroughly?\n            [Confirm that every line of code has been carefully examined for potential issues.]\n9. Context and Impact:\n            Have the broader context and impact of the changes been considered?\n            [Assess the impact of the changes on the overall system and provide feedback.]\n10. Good Practices:            \n            Highlight any positive aspects or good practices observed in the changes.\n            [Acknowledge and commend any particularly well-implemented solutions or practices.]\nAdditional Comments:      \n            [Add any additional comments or suggestions not covered in the above sections.]\nOverall Assessment:           \n            [Provide an overall assessment of the changes and whether they are ready for approval.]\nReview Decision:            \n            [Choose one: Approve / Approve with Changes / Request Changes / Hold / Other]\nNext Steps:\n            [Outline any next steps or actions required based on the review decision.]"

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








