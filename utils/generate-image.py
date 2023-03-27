import requests
import time
import os
import dotenv
import openai

dotenv.load_dotenv()

api_base = 'https://meyerperin-openai.openai.azure.com/'
api_key = os.getenv("OPENAI_API_PERSONAL_KEY")
api_version = '2022-08-03-preview'

url = "{}dalle/text-to-image?api-version={}".format(api_base, api_version)
headers= { "api-key": api_key, "Content-Type": "application/json" }
body = {
    "caption": "white siamese cat sitting on a wooden floor",
#    "n":2,
    "resolution": "1024x1024"
}

submission = requests.post(url, headers=headers, json=body)
print(submission)

operation_location = submission.headers['Operation-Location']
retry_after = submission.headers['Retry-after']
status = ""
while (status != "Succeeded"):
    time.sleep(int(retry_after))
    response = requests.get(operation_location, headers=headers)
    status = response.json()['status']
image_url = response.json()['result']['contentUrl']

print(image_url)

# openai.api_type = "azure"
# openai.api_base = "https://meyerperin-openai.openai.azure.com/"
# openai.api_version = "2022-08-03-preview"
# openai.api_key = os.getenv("OPENAI_API_PERSONAL_KEY")

# def generate_image(caption, n=1, resolution="1024x1024"):
#     response = openai.Image.create(
#         engine="dalle",
#         prompt=caption,
#         resolution=resolution
#     )

#     print(response)
#     return response['choices'][0]['text']

# generate_image("white siamese cat sitting on a wooden floor")