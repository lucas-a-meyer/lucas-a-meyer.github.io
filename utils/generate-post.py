import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://eastus.api.cognitive.microsoft.com/"
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def generate_post(subject):
    response = openai.Completion.create(
        engine="gpt-35-turbo",
        prompt=f"""
        <|im_start|>system\nAssistant is a tool that helps influencers improve their reach<|im_end|>\n
        <|im_start|>user\nGenerate a four paragraph blog post about {subject}<|im_end|>\n
        <|im_start|>user\nTry to be a little funny and hopeful<|im_end|>\n
        <|im_start|>assistant\n
        """,
        temperature=0.5,
        max_tokens=4096,
        top_p=1,
        stop=["<|im_end|>"])

    return response['choices'][0]['text']        

print(generate_post("I'm feeling overwhelmed about how many new AI launches are happening, but I think that AI will not replace us, people who use AI will, and therefore I'm learning as much as I can"))