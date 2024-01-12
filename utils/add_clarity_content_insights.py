import yaml
import re
import os
from openai import OpenAI

from dotenv import load_dotenv

def recompose_qmd(yaml_data, original_yaml, content):
    # Convert the modified YAML data to string
    new_yaml_str = yaml.dump(yaml_data, default_flow_style=False)

    # replace the *second* appearence of --- with ---\n\n<article data-clarity-region="article">
    content = content.replace('---', '---\n\n<article data-clarity-region="article">', 1)

    # Replace the original YAML content with the new one
    updated_content = content.replace(original_yaml, new_yaml_str)
    updated_content += '</article>'
    return updated_content


def parse_qmd(content):
    # Extract the YAML front matter
    matches = re.findall(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not matches:
        return None, None
    return matches[0], content

def process_qmd_files(directory):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.qmd'):
            
            # Skip files that are not visible
            if filename.startswith('_'):
                continue

            print(f'Processing {filename}...')
            file_path = os.path.join(directory, filename)

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            original_yaml, full_content = parse_qmd(content)
            markdown = full_content.replace(original_yaml, '')

            if original_yaml is None:
                print(f'No YAML front matter found in {filename}, skipping...')
                continue  # Skip files without YAML front matter

            yaml_data = yaml.safe_load(original_yaml)            
            
            # Recompose the file content
            updated_content = recompose_qmd(yaml_data, original_yaml, full_content)

            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)



load_dotenv()

# Specify the directory containing your .qmd files
directory = 'posts'

# Process all .qmd files in the directory
process_qmd_files(directory)
