import openai
import time
import os

RATE_LIMIT = 20
MODEL = 'gpt-3.5-turbo'

openai.api_key = os.getenv("OPENAI_API_KEY")

def send_message(prompt, user_messages, time_limit_rate=RATE_LIMIT):
    # Create a context with prompt and user message
    context = [{'role': 'system', 'content': prompt}] + [{'role':'user','content':message} for message in user_messages]
    
    # Send the context to the ChatCompletion API
    response = openai.ChatCompletion.create(model=MODEL, messages=context)
    
    # Get the response text from the API response
    response_text = response.choices[0].message["content"]

    ### for debugging
    print(f"""
{prompt}
############
{user_messages}
------------
{response_text}
""")
    ###

    # Add a time delay to stay within the rate limit
    time.sleep(time_limit_rate)
    
    # Return the response text
    return response_text