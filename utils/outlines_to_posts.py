# For each file in the outlines directory, create a post in the posts directory

import os
import re
import openai
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
from azure.storage.blob import BlobServiceClient
import os

# Load the environment variables
load_dotenv()

# Set the OpenAI API key
openai.api_type = "azure"
openai.api_base = "https://meyerperin-openai.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_PERSONAL_KEY")


def generate_image(image_prompt, image_path, image_filename):
    pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1-base").to("cuda")
    style = """illustration, high detail, realistic shaded lighting by ilya kuvshinov and michael garmash and rob rey, 
        iamag premiere, wlop matte print, 8k resolution, a masterpiece"""
    negative_prompt = """ugly, low detail, extra limbs, malformed limbs, poorly drawn hands"""
    image = pipeline(prompt=f"{image_prompt}, {style}", negative_prompt=negative_prompt, height=512, width=512, num_inference_steps=72, guidance_scale=6.5).images[0]
    image_filename = f"diffused_{image_filename}.png"
    image.save(os.path.join(image_path, image_filename), format="PNG", overwrite=True)

def upload_image_to_azure_storage(image_path, image_filename):
    # Replace with your connection string
    connection_string = os.getenv("AZURE_STORAGE_CONN")

    # Replace with your container name
    container_name = "blog-images"

    # Replace with the path to your local file
    local_file_path = os.path.join(image_path, image_filename)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(image_filename)

    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)    


def outline_to_post_text(outline):
    message_list = [
        {"role":"system","content":"You are a professional writer that likes writing about Business, Finance and Economics"},
        {"role":"user","content":"[Voice and style guide: Use a convincing tone, rhetorical questions, and stories to keep the reader interested. Use similes, metaphors, and other literary tools to make your points easier to understand and remember. [Write in a way that is both educational and fun.]]"},
        {"role":"user","content":"Write like a graduate level english major"},
        {"role":"user","content":"Don't talk about yourself"},
        {"role":"user","content":"Expand the following outline into a LinkedIn post:"},
        {"role":"user","content": outline},
        {"role":"assistant","content":""},
    ]

    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages = message_list, 
        temperature = 0.9
    )

    return response.choices[0].message.content

def create_title_from_post_text(post_text):
    message_list = [
        {"role":"system","content":"You are a professional writer with a graduate level education in English and a background in Business, Finance and Economics"},
        {"role":"user","content":"Create a title for the article below"},
        {"role":"user","content":"The title should be catchy and informative, just a single line, less than 60 characters"},
        {"role":"user","content": post_text},
        {"role":"assistant","content":"Title:"},
    ]

    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages = message_list, 
        temperature = 0.9
    )

    return response.choices[0].message.content    

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)

# Get the outlines directory
outlines_dir = os.path.join(parent_dir, 'outlines')

# Get the posts directory
posts_dir = os.path.join(parent_dir, 'posts')

# images directory
images_dir = os.path.join(parent_dir, 'local_data')

# Get the list of files in the outlines directory
outlines = os.listdir(outlines_dir)

# For each file in the outlines directory
for outline in outlines:
    # Skip the README file
    if outline == 'README':
        continue

    # Get the full path to the file
    outline_path = os.path.join(outlines_dir, outline)

    # Open the file
    with open(outline_path, 'r') as f:

        # the date is the first line of the file, read it
        date = f.readline()

        # Remove the newline character
        date = date.replace('\n', '')

        # The image prompt is the second line, read it
        image_prompt = f.readline()
        image_prompt = image_prompt.replace('\n', '')

        # The image name is on the third line, read it
        image_name = f.readline()
        image_name = image_name.replace('\n', '')

        # Generate the image
        generate_image(image_prompt, images_dir, image_name)

        # The outline is the remainder of the file
        outline = f.read()

        # Create the post test from the outline
        post_text = outline_to_post_text(outline)
        title = create_title_from_post_text(post_text)

        # remove quotes and newlines from title
        title = title.replace('\n', '')
        title = title.replace('"', '')
       
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title).lower()

        # if there's a leading dash, remove it
        if slug[0] == '-':
            slug = slug[1:]

        # if there's a trailing dash, remove it
        if slug[-1] == '-':
            slug = slug[:-1]

        slug = f"{date}-{slug}"

        # Get the filename
        filename = f'{slug}.qmd'

        # Get the full path to the file
        post_path = os.path.join(posts_dir, filename)

        # Upload the image to Azure
        upload_image_to_azure_storage(images_dir, f"diffused_{image_name}.png")

        # Create the post
        with open(post_path, 'w') as f:
            # Write the post
            f.write('---\n')
            f.write("author: Lucas A. Meyer, GPT-3.5, Stable Diffusion 2.1\n")
            f.write(f'title: "{title}"\n')
            f.write(f"date: {date} 06:00:00\n")
            f.write(f"linkedin-target-date: {date} 07:01:00\n")
            f.write(f"twitter-target-date: {date} 07:01:00\n")
            f.write(f"draft: false\n")
            f.write(f"image: https://mpsocial.blob.core.windows.net/blog-images/diffused_{image_name}.png\n")
            f.write(f"include-in-header: _msft-clarity.html\n")
            f.write('---\n\n')
            f.write(post_text)

# delete all files from the outlines directory
for outline in outlines:

    # Skip the README file
    if outline == 'README':
        continue

    outline_path = os.path.join(outlines_dir, outline)
    os.remove(outline_path)


