from fastapi import APIRouter, HTTPException
import google.generativeai as genai
from models.chat_bot import ChatRequest,CodeReviewContext
from config.chatbot_config import generation_config, safety_settings

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest", 
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat_bot_router = APIRouter()


review_data_store = {
    "code": "",
    "review_content": "",
    "suggestion_content": "",
    "refer_links_content": ""
}

@chat_bot_router.post("/review-data")
async def initiate_code(context: CodeReviewContext):
    try:
        # Update the dictionary with the context data
        review_data_store["code"] = context.selectedFileContent
        review_data_store["review_content"] = context.reviewContent
        review_data_store["suggestion_content"] = context.suggestionContent
        review_data_store["refer_links_content"] = context.referLinksContent
        
        # For illustration, we're just printing it
        print("Code:", review_data_store["code"])
        print("Review Content:", review_data_store["review_content"])
        print("Suggestion Content:", review_data_store["suggestion_content"])
        print("Reference Links Content:", review_data_store["refer_links_content"])
        
        return {"Status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process the code review context")

# code = "def fibonacci_sequence(n):\n    sequence = [0, 1]\n    for i in range(2, n):\n        sequence.append(sequence[i - 1] + sequence[i - 2])\n    return sequence\n\ndef main():\n    num_terms = input(\"Enter the number of terms in the Fibonacci sequence: \")\n    if num_terms.isdigit():\n        num_terms = int(num_terms)\n        if num_terms <= 0:\n            print(\"Number of terms must be positive.\")\n            return\n        fib_sequence = fibonacci_sequence(num_terms)\n        print(\"Fibonacci sequence:\")\n        for term in fib_sequence:\n            print(term, end=\", \")\n        print()\n    else:\n        print(\"Please enter a valid integer.\")\n\nmain()\n\n"
# review = "Strengths:Modularity: The code is organized into separate functions for generating the Fibonacci sequence (fibonacci_sequence) and for handling user input and printing (main). This enhances readability and maintainability.Input Validation: It checks whether the user input is a valid integer before proceeding to generate the Fibonacci sequence, preventing potential errors.Error Handling: It handles cases where the user inputs non-positive integers gracefully and prompts the user to enter a valid integer.Efficient Fibonacci Generation: It efficiently generates the Fibonacci sequence using a loop rather than recursion, which can be more resource-intensive for large values of n.Areas for Improvement:Handling Edge Cases: The fibonacci_sequence function does not handle the case when n is less than or equal to 1. It should return [0] when n is 0 and [0, 1] when n is 1.User Instructions: The prompt for the number of terms in the Fibonacci sequence could be clearer. For example, it could specify that the user needs to input a positive integer.Printing: The code prints the Fibonacci sequence with a trailing comma after each term. This might not be desirable. You could consider joining the terms into a string and printing them without the trailing comma.Variable Naming: The variable num_terms could be more descriptive. Since it represents the number of terms in the sequence, perhaps num_sequence_terms would be clearer.Overall:The code is well-structured and functional, but it could be improved by addressing the mentioned areas for improvement, particularly in handling edge cases and enhancing user instructions."
# suggestions = ""
clause_prompt = "use give code, review, suggestions, reference links & any topics about programming to answer questions. don't answer anything outside this domain. Just responde 'It's outside from my domain'"
# prompt = f"This is m''y code: {code}. This is my code review: {review}. And these are the suggestion for my code: {suggestions}. Study this code, code review and suggestion. Don't reply this. "
prompt = f"This is my code: {review_data_store["code"]}. This is my code review: {review_data_store["review_content"]}, This is the suggestions gave for the code: {review_data_store["suggestion_content"]} and These are the reference link give for further study :{review_data_store["refer_links_content"]}. Study this code, code review and suggestions and reference links. Don't reply this. "

chat_history = [
    {
        "role": "user",
        "parts": [prompt]
    },
    {
        "role": "user",
        "parts": ["User above content to answer follow quetions. Don't asnwer anythin outside from this domain. if anythin ask outside the domain give the respond it's outside from my domain "]
    },
    {
        "role": "model",
        "parts": ["Okay, "]
    },
]



    

@chat_bot_router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    print(prompt)
    
    message = chat_request.message
    
    msg_text = clause_prompt + " " + message

    # Append the new user message to the chat history
    chat_history.append({"role": "user", "parts": [msg_text]})

    # Generate the response from the AI model
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(msg_text)
    model_reply = response.text

    # Append the AI model's response to the chat history
    chat_history.append({"role": "model", "parts": [model_reply]})

    return {"reply": model_reply}