import os
from dotenv import load_dotenv

# Load the variables from .env into environment variables
load_dotenv()

# Now you can access them using os.getenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example request with specified hyperparameters
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{
        "role": "user",
        "content": "Hello! How are you doing today?"
    }],
    temperature=1,           # Zero temperature for deterministic output
    top_p=1,                 # Ensures no sampling from token distribution
    frequency_penalty=0      # No penalty for repeated phrases
    # presence_penalty=0.3     # Slight penalty to encourage topic diversity
)

print(f'AI response:\n{response.choices[0].message.content}')
