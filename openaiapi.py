import openai
import asyncio
import os

RATE_LIMIT = 20
MODEL = 'gpt-3.5-turbo'

openai.api_key = os.getenv("OPENAI_API_KEY")

async def send_messages(prompt, user_messages, time_limit_rate=RATE_LIMIT):
    # Create a context with prompt and user message
    context = [{'role': 'system', 'content': prompt}] + [{'role':'user','content':message} for message in user_messages]
    
    # Send the context to the ChatCompletion API
    response = await openai.ChatCompletion.acreate(model=MODEL, messages=context)
    
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

    # Add a asyncio delay to stay within the rate limit
    asyncio.sleep(time_limit_rate)
    
    # Return the response text
    return response_text

async def send_message(txt, time_limit_rate=RATE_LIMIT):
    # Create a context with prompt and user message
    context = [{'role': 'user', 'content': txt}]
    
    # Send the context to the ChatCompletion API
    response = await openai.ChatCompletion.acreate(model=MODEL, messages=context)
    
    # Get the response text from the API response
    response_text = response.choices[0].message["content"]

    ### for debugging
    print(f"""
{txt}
############
{response_text}
""")
    ###

    # Add a time delay to stay within the rate limit
    asyncio.sleep(time_limit_rate)
    
    # Return the response text
    return response_text