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
openai.api_base = os.getenv("OPENAI_ENDPOINT")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = "gpt-4"

def generate_image(image_prompt, image_path, image_name):
    
    # Generate filename: 
    image_filename = f"diffused_{image_name}.png"

    # Check if the image already exists
    if os.path.exists(os.path.join(image_path, image_filename)):
        print(f"Image {image_filename} already exists, skipping...")
        return
    else:
        print(f"Generating image {image_filename} with prompt {image_prompt}...")
    
    pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1-base").to("cuda")
    style = """illustration, high detail, realistic shaded lighting by ilya kuvshinov and michael garmash and rob rey, 
        # iamag premiere, wlop matte print, 8k resolution, a masterpiece"""
    # style = """high quality photography,
    #     3 point lighting, flash with softbox, by Annie Leibovitz, 80mm, hasselblad, Canon EOS R3"""
    negative_prompt = """ugly, low detail, extra limbs, malformed limbs, poorly drawn hands"""

    image = pipeline(prompt=f"{image_prompt}, {style}", negative_prompt=negative_prompt, height=512, width=512, num_inference_steps=72, guidance_scale=6.5).images[0]
    image.save(os.path.join(image_path, image_filename), format="PNG", overwrite=True)

    return image_filename

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

def outline_to_post_text(openai_model, outline, temperature=0.4):
    message_list = [
        {"role":"system","content":"You are a Wall Street Journal reporter that also knows technology and finance, like Walt Mossberg"},
        {"role":"user","content":"Voice and style guide: Use a convincing tone, similes, and stories to keep the reader interested."},
        {"role":"user","content":"Use metaphors, and other literary tools to make your points easier to understand and remember."},
        {"role":"user","content":" Write in a way that is both educational and fun, but keep it professional."},
        {"role":"user","content":"Don't talk about yourself"},
        {"role":"user","content":"The first paragraph should be short and catchy"},
        {"role":"user","content":"Expand the following outline into a LinkedIn post:"},
        {"role":"user","content": outline},
        {"role":"assistant","content":""},
    ]

    response = openai.ChatCompletion.create(
        engine=openai_model,
        messages = message_list, 
        temperature = temperature
    )

    return response.choices[0].message.content

def improve_text(openai_model, text, temperature=0.4):
    message_list = [
        {"role":"system","content":"You are a Wall Street Journal reporter that also knows technology and finance, like Walt Mossberg"},
        {"role":"user","content":"Voice and style guide: Use a convincing tone, similes, and stories to keep the reader interested."},
        {"role":"user","content":"Use metaphors, and other literary tools to make your points easier to understand and remember."},
        {"role":"user","content":" Write in a way that is both educational and fun, but keep it professional."},
        {"role":"user","content":"Don't talk about yourself"},
        {"role":"user","content":"Improve the text below and make it a better blog post that can be posted to LinkedIn:"},
        {"role":"user","content": text},
        {"role":"assistant","content":""},
    ]

    response = openai.ChatCompletion.create(
        engine = openai_model,
        messages = message_list, 
        temperature = temperature
    )

    return response.choices[0].message.content

def create_title_from_post_text(openai_model, post_text, temperature=0.4):
    message_list = [
        {"role":"system","content":"You are a professional writer with a graduate level education in English and a background in Business, Finance and Economics"},
        {"role":"user","content":"Create a title for the article below"},
        {"role":"user","content":"The title should be catchy and informative, just a single line, less than 60 characters"},
        {"role":"user","content": post_text},
        {"role":"assistant","content":"Title:"},
    ]

    response = openai.ChatCompletion.create(
        engine=openai_model,
        messages = message_list, 
        temperature = temperature
    )

    title = response.choices[0].message.content    
    # remove quotes and newlines from title
    title = title.replace('\n', '')
    title = title.replace('"', '')

    return title   

def generate_slug_from_title(title):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title).lower()

    # if there's a leading dash, remove it
    if slug[0] == '-':
        slug = slug[1:]

    # if there's a trailing dash, remove it
    if slug[-1] == '-':
        slug = slug[:-1]

    return slug

def get_directories():
    
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

    return outlines_dir, posts_dir, images_dir

def delete_processed_files():
    # delete all files from the outlines directory
    for outline in outlines:

        # Skip the README file
        if outline.startswith('TEMPLATE'):
            continue

        outline_path = os.path.join(outlines_dir, outline)
        os.remove(outline_path)

def create_header(title, date, image_file_name):
    header = f"""---
author: Lucas A. Meyer, GPT-3.5, Stable Diffusion 2.1
title: {title}
date: {date} 06:00:00
linkedin-target-date: {date} 07:01:00
twitter-target-date: {date} 07:01:00
draft: false
image: https://mpsocial.blob.core.windows.net/blog-images/{image_file_name}
include-in-header: _msft-clarity.html
---\n\n"""
    return header
 
outlines_dir, posts_dir, images_dir = get_directories()

# Get the list of files in the outlines directory
outlines = os.listdir(outlines_dir)

# For each file in the outlines directory
for outline in outlines:

    # Skip the TEMPLATE files
    if outline.startswith('TEMPLATE'):
        continue

    # Get the full path to the file
    outline_path = os.path.join(outlines_dir, outline)

    # Open the file
    with open(outline_path, 'r') as f:

        # the date is the first line of the file, read it
        date = f.readline().replace('\n', '')

        # The image prompt is the second line, read it
        image_prompt = f.readline().replace('\n', '')

        # The image name is on the third line, read it
        image_name = f.readline().replace('\n', '')

        # Generate the image
        image_file_name = generate_image(image_prompt, images_dir, image_name)

        # Upload the image to Azure
        upload_image_to_azure_storage(images_dir, image_file_name)        

        # The next line contains the verb explaining what we are supposed to do with the file
        verb = f.readline().strip()

        # The fifth line has the main text
        text = f.read()

        if verb.lower() == 'expand':
            post_text = outline_to_post_text(openai_model, text, 0.2)
        elif verb.lower() == 'improve':
            post_text = improve_text(openai_model, text)
    
        print(f"Generated text:\n{post_text}")

        # File name
        title = create_title_from_post_text("gpt-35-turbo", post_text)      
        slug = generate_slug_from_title(title)
        filename = f"{date}-{slug}.qmd"

        # Get the full path to the file
        post_path = os.path.join(posts_dir, filename)

        # delete files starting with the date
        for file in os.listdir(posts_dir):
            if file.startswith(date):
                os.remove(os.path.join(posts_dir, file))

        # Create the post
        with open(post_path, 'w') as f:
            # Write the post
            header = create_header(title, date, image_file_name)

            f.write(header)
            f.write(post_text)

    # Clean up
    delete_processed_files()