import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://eastus.api.cognitive.microsoft.com/"
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPEN_AI_API_KEY")

def generate_post(subject, start="", end="", assistant="a tool that helps influencers improve their reach"):
    response = openai.Completion.create(
        engine="gpt-35-turbo",
        prompt=f"""
        <|im_start|>system\nAssistant is {assistant}<|im_end|>\n
        <|im_start|>user\nGenerate an essay about {subject}<|im_end|>\n
        <|im_start|>user\nUse professional language<|im_end|>\n
        <|im_start|>user\nWrite in the style of Michael Lewis Moneyball<|im_end|>\n
        <|im_start|>user\nYour essay should start with "{start}"<|im_end|>\n
        <|im_start|>user\nYour essay should end with "{end}"<|im_end|>\n
        <|im_start|>user\nDo not start paragraphs with "In conclusion"<|im_end|>\n
        <|im_start|>assistant\n
        """,
        temperature=0.5,
        max_tokens=4096,
        top_p=1,
        stop=["<|im_end|>"])

    return response['choices'][0]['text']        

assistant = "a helpful editor that can help you write a blog post"

about = "how chesterton's fence can help a person who just joined a team to be more efficient"

about = "Dan Gilbert's experiment where people decided that it was better to shock themselves than to be alone with their thoughts"

about = "The importance of programmers and analysts learning what and how to delegate tasks to large language models"
start = "In my career, I have worked as an individual contributor and as a manager. With large language models, "
end = "If you are technically oriented and used to do everything yourself, you may find that learning to cede some control to LLMs is going to make you a lot more productive. "

print(generate_post(subject=about, start=start, end=end, assistant=assistant))