import yaml
import re
import os

def parse_qmd(content):
    # Extract the YAML front matter
    matches = re.findall(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not matches:
        return None, None
    return matches[0], content

def recompose_qmd(yaml_data, original_yaml, content):
    # Convert the modified YAML data to string
    new_yaml_str = yaml.dump(yaml_data, default_flow_style=False)

    # Replace the original YAML content with the new one
    updated_content = content.replace(original_yaml, new_yaml_str)
    return updated_content

def process_qmd_files(directory):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.qmd'):
            print(f'Processing {filename}...')

            file_path = os.path.join(directory, filename)

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            original_yaml, full_content = parse_qmd(content)

            if original_yaml is None:
                continue  # Skip files without YAML front matter

            yaml_data = yaml.safe_load(original_yaml)

            # Modify the yaml_data as needed
            if 'id' in yaml_data:
                del yaml_data['id']

            if 'linkedin-linkback' in yaml_data:
                del yaml_data['linkedin-linkback']

            if 'linkedin-posted' in yaml_data:
                del yaml_data['linkedin-posted']
            
            if 'linkedin-target-date' in yaml_data:
                del yaml_data['linkedin-target-date']

            if 'linkedin-url' in yaml_data:
                del yaml_data['linkedin-url']

            if 'post-url' in yaml_data:
                del yaml_data['post-url']

            if 'tweet-url' in yaml_data:
                del yaml_data['tweet-url']

            if 'twitter-description' in yaml_data:
                del yaml_data['twitter-description']

            if 'twitter-posted' in yaml_data:
                del yaml_data['twitter-posted']

            if 'twitter-target-date' in yaml_data:
                del yaml_data['twitter-target-date']

            if 'linkedin-link' in yaml_data:
                del yaml_data['linkedin-link']

            if 'twitter-link' in yaml_data:
                del yaml_data['twitter-link']

            if 'twitter-repost' in yaml_data:
                del yaml_data['twitter-repost']

            if 'linkedin-repost' in yaml_data:
                del yaml_data['linkedin-repost']

            # Recompose the file content
            updated_content = recompose_qmd(yaml_data, original_yaml, full_content)

            # Write the updated content back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

# Specify the directory containing your .qmd files
directory = 'posts'

# Process all .qmd files in the directory
process_qmd_files(directory)
