from diffusers import StableDiffusionPipeline
from azure.storage.blob import BlobServiceClient
import os

def generate_image(image_prompt, image_path, image_name):
    
    # Generate filename: 
    image_filename = f"diffused_{image_name}.png"

    # Check if the image already exists
    if os.path.exists(os.path.join(image_path, image_filename)):
        print(f"Image {image_filename} already exists, skipping...")
        return image_filename
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

def upload_image_to_azure_storage(image_path: str) -> str:
    
    # Connection settings
    connection_string = os.getenv("AZURE_STORAGE_CONN")
    container_name = "blog-images"
    storage_base_url = f"https://mpsocial.blob.core.windows.net/"

    # Get the filename from the path
    image_filename = os.path.basename(image_path)
    
    # Connect to the blob service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(image_filename)

    # Upload the image
    with open(image_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)    

    # Return the image URL
    return f"{storage_base_url}{container_name}/{image_filename}"
    
