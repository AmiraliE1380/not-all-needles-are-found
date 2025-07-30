import os
from dotenv import load_dotenv

# Load the variables from .env into environment variables
load_dotenv()

# Now you can access them using os.getenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example request with specified hyperparameters
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Hello! How long can the context of famous LLMs like latest versions of OpenAI models, or Gemini's latest model be? Tell me how many tokens? Please search if you don't have the information."
    }],
    temperature=0,           # Zero temperature for deterministic output
    top_p=1,                 # Ensures no sampling from token distribution
    frequency_penalty=0,     # No penalty for repeated phrases
    presence_penalty=0.3     # Slight penalty to encourage topic diversity
)

print(f'AI response:\n{response.choices[0].message.content}')


openai_models = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo-2024-04-09",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4-0613",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-instruct",
    "o1",
    "o1-mini",
    "o1-pro",
    "o3-mini",
    "o3",
    "o3-pro"
]