import os
from dotenv import load_dotenv

# Load the variables from .env into environment variables
load_dotenv()

# Now you can access them using os.getenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example request
response = client.chat.completions.create(model="gpt-4o",
messages=[{"role": "user", "content": "Hello! How long can the context of famous LLMs like latest versions of OpenAI models, or Gemini's latest model be? Tell me how many tokens? Please search if you don't have the information."}])

print(response.choices[0].message.content)
