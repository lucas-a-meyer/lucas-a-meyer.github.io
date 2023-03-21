import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://eastus.api.cognitive.microsoft.com/"
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def generate_post(subject, assistant="a tool that helps influencers improve their reach"):
    response = openai.Completion.create(
        engine="gpt-35-turbo",
        prompt=f"""
        <|im_start|>system\nAssistant is {assistant}<|im_end|>\n
        <|im_start|>user\nGenerate a blog post about {subject}<|im_end|>\n
        <|im_start|>user\nUse professional language, this will be posted to LinkedIn<|im_end|>\n
        <|im_start|>user\nWrite in the style of Michael Lewis and Hemingway<|im_end|>\n
        <|im_start|>user\nYour output should be ready to paste in a blog post<|im_end|>\n
        <|im_start|>assistant\n
        """,
        temperature=0.5,
        max_tokens=4096,
        top_p=1,
        stop=["<|im_end|>"])

    return response['choices'][0]['text']        

about = "how chesterton's fence can help a person who just joined a team to be more efficient"
about = "Dan Gilbert's experiment where people decided that it was better to shock themselves than to be alone with their thoughts"


assistant = "the editor of a major newspaper, who is also the CEO of a tech company"
print(generate_post(subject=about, assistant=assistant))