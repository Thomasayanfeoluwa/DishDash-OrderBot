from openai import OpenAI
import os

client = OpenAI()

message = [
    {"role": "system", "content": system_instruction}
]

def ask_order(message, model=)

response = client.responses.create(
    input="Explain the importance of fast language models",
    model="openai/gpt-oss-20b",
)
print(response.output_text)

