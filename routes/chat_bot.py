from fastapi import APIRouter
import google.generativeai as genai
from config import config
from models.chat_bot import ChatRequest



genai.configure(api_key=config.Configurations.gemini_api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat_bot_router = APIRouter()

@chat_bot_router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    convo = model.start_chat(history=[
      {  "role": "user",
    "parts": ["Userdef fibonacci_sequence(n):\n    sequence = [0, 1]\n    for i in range(2, n):\n        sequence.append(sequence[i - 1] + sequence[i - 2])\n    return sequence\n\ndef main():\n    num_terms = input(\"Enter the number of terms in the Fibonacci sequence: \")\n    if num_terms.isdigit():\n        num_terms = int(num_terms)\n        if num_terms <= 0:\n            print(\"Number of terms must be positive.\")\n            return\n        fib_sequence = fibonacci_sequence(num_terms)\n        print(\"Fibonacci sequence:\")\n        for term in fib_sequence:\n            print(term, end=\", \")\n        print()\n    else:\n        print(\"Please enter a valid integer.\")\n\nmain()\n\nthis is my code and below is the review for it\n\nStrengths:Modularity: The code is organized into separate functions for generating the Fibonacci sequence (fibonacci_sequence) and for handling user input and printing (main). This enhances readability and maintainability.Input Validation: It checks whether the user input is a valid integer before proceeding to generate the Fibonacci sequence, preventing potential errors.Error Handling: It handles cases where the user inputs non-positive integers gracefully and prompts the user to enter a valid integer.Efficient Fibonacci Generation: It efficiently generates the Fibonacci sequence using a loop rather than recursion, which can be more resource-intensive for large values of n.Areas for Improvement:Handling Edge Cases: The fibonacci_sequence function does not handle the case when n is less than or equal to 1. It should return [0] when n is 0 and [0, 1] when n is 1.User Instructions: The prompt for the number of terms in the Fibonacci sequence could be clearer. For example, it could specify that the user needs to input a positive integer.Printing: The code prints the Fibonacci sequence with a trailing comma after each term. This might not be desirable. You could consider joining the terms into a string and printing them without the trailing comma.Variable Naming: The variable num_terms could be more descriptive. Since it represents the number of terms in the sequence, perhaps num_sequence_terms would be clearer.Overall:The code is well-structured and functional, but it could be improved by addressing the mentioned areas for improvement, particularly in handling edge cases and enhancing user instructions.\n\nu should ansewer questions user ask  according to this code and the review  above"]
  },
  {
    "role": "model",
    "parts": ["Okay, I'm ready to answer your questions about the Python code and the provided review. I'll do my best to provide insights and explanations based on the code's functionality and the suggestions mentioned in the review. Feel free to ask anything specific or request further improvements!"]
  },

        {
            "role": "user",
            "parts": [chat_request.message]
        },
        {
            "role": "model",
            "parts": ["Okay, I'm ready to answer your questions about the Python code and the provided review. I'll do my best to provide insights and explanations based on the code's functionality and the suggestions mentioned in the review. Feel free to ask anything specific or request further improvements!"]
        },
    ])

    convo.send_message(chat_request.message)
    return {"reply": convo.last.text}