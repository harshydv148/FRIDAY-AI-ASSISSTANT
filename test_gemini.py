import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",   # ✅ latest working
    messages=[
        {"role": "user", "content": "Explain AI in one line"}
    ]
)

print(response.choices[0].message.content)