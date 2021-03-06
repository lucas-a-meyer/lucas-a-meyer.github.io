### This is the engine that 
###    - Goes through posts
###    - Determines whether to remove them from draft
###    - Determines whether to post them to LinkedIn and/or Twitter
###    - Posts them to LinkedIn/Twitter

import sys
import os
from bs4 import BeautifulSoup
from markdown import markdown
import re
import yaml
import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from azure.cosmos import CosmosClient
import hashlib
import json
from typing import List

def update_lucas(body):

    account_sid = os.getenv("TWILIO_ACCOUNT_ID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to="+14258776991",
        from_="+19783965634",
        body=body
    )

def generate_cosmos_id(filepath):
    h = hashlib.md5(filepath.encode())
    return h.hexdigest()

def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # Remove YAML
    yml = re.match(r"---.*?---", markdown_string, re.DOTALL).group(0)
    markdown_string = re.sub(r"---.*?---", '', markdown_string, 0, re.DOTALL)  

    # Remove markdown code blocks
    markdown_string = re.sub(r"```.*?```", '', markdown_string, 0, re.DOTALL)

    # Remove commentary
    markdown_string = re.sub(r"<!--.*?-->", '', markdown_string, 0, re.DOTALL)
    
    # Remove formatting newlines
    # markdown_string = re.sub(r"\n([^-])", r'\g<1>\n', markdown_string, 0, re.DOTALL)

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', r'\g<1>', html)
    html = re.sub(r'<code>(.*?)</code>', r'\g<1>', html)
    html = re.sub(r'\$\$(.*?)\$\$', '', html, 0, re.DOTALL)

    # Remove headings
    html = re.sub(r'<h1>(.*?)</h1>', ' ', html)
    html = re.sub(r'<h2>(.*?)</h2>', ' ', html)
    html = re.sub(r'<h3>(.*?)</h3>', ' ', html)
    html = re.sub(r'<h4>(.*?)</h4>', ' ', html)
    html = re.sub(r'<h5>(.*?)</h5>', ' ', html)

    # recreate lists
    html = re.sub(r'<li>(.*?)</li>', r'- \g<1>', html)
    
    # Remove Quarto markdown options
    html = re.sub(r'{(.*?)}', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return yml, text

def get_file_plaintext(filepath):
    with open(filepath) as f:
        yml, plaintext = markdown_to_text(f.read())
        plaintext = re.sub(r"\n", '\n\n', plaintext, 0, re.DOTALL)
        plaintext = re.sub(r"\n\n\n", '\n\n', plaintext, 0, re.DOTALL)
        plaintext = re.sub(r"\n\n-", '\n-', plaintext, 0, re.DOTALL)
        plaintext = re.sub(r"\n\n\n", '\n\n', plaintext, 0, re.DOTALL)
        plaintext = re.sub(r"\n\n\n", '\n\n', plaintext, 0, re.DOTALL)
        plaintext = re.sub(r"\n\n\n", '\n\n', plaintext, 0, re.DOTALL)
        return yml, plaintext

def get_md_content(filepath):
    with open(filepath, "r") as f:
        file_contents = f.read()

    pos1 = file_contents.find("---\n")
    pos2 = file_contents.find("---\n", pos1+1)
    return file_contents[pos2+4:]

def update_front_matter(filepath, new_front_matter_dict):
    new_yml = yaml.dump(new_front_matter_dict)
    new_yml = f"---\n{new_yml}---\n"
    new_file_content = new_yml + get_md_content(filepath)
    with open(filepath, "w") as f:
        f.write(new_file_content)

def convert_to_utc(local_time: datetime.datetime) -> datetime: 
    ts = datetime.datetime.timestamp(local_time)
    return datetime.datetime.utcfromtimestamp(ts) # This is the old way

def convert_cosmos_utc_to_local(cosmos_utc_time: str) -> datetime:
    input_time = cosmos_utc_time[:-2]
    dtUTC = datetime.datetime.strptime(input_time, "%Y-%m-%dT%H-%M-%S.%f")
    dtZone = dtUTC.replace(tzinfo = datetime.timezone.utc)
    dtLocal = dtZone.astimezone()
    return dtLocal

def cosmos_date_format(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H-%M-%S.%f0Z")

def my_cosmos_client(db, container):
    COSMOS_URI = os.environ["COSMOS_URI"]
    COSMOS_KEY = os.environ["COSMOS_KEY"]

    client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
    database = client.get_database_client(db)
    return database.get_container_client(container)
    
def get_cosmos_record(cc, id):

    item_count = 0
    cosmos_record = {}
 
    q = f"SELECT * FROM container c where c.id = '{id}'"

    for item in cc.query_items(query=q, enable_cross_partition_query=True):
        item_count = item_count + 1
        cosmos_record = item

    if item_count > 1:
        raise IndexError
    else:
        return cosmos_record

def remove_fields_from_dict(d: dict, list_of_fields: List[str]) -> dict:
    for field in list_of_fields:
        if field in d: d.pop(field)
    return d


def process_file(filepath):
    print(f"Processing {filepath}")

    # Get local configuration from YAML file
    yml, txt = get_file_plaintext(filepath)
    front_matter_dict = yaml.safe_load(yml.replace("---", ""))   

    # ID is a hash
    id = generate_cosmos_id(filepath)
    
    # Get the cosmos record with that ID
    cc = my_cosmos_client("social-media", "blog-posts")

    # If there's a key called reset, we'll rewrite the remote data
    reset = front_matter_dict.get("reset")
    if reset:
        cosmos_record = {}
    else:
        cosmos_record = get_cosmos_record(cc, id)
    
    # Now I have two dicts: cosmos_record with the remote data, front_matter_dict with the local data
    # rules: 
    #   - cosmos_record dates should be in UTC
    #   - front_matter_dict dates should be local
    #   - front_matter_dict shouldn't have the 'linkedin-body' and the 'twitter-body' fields

    # Check that we have Microsoft Clarity installed in the page
    if not front_matter_dict.get("include-in-header"):
        front_matter_dict["include-in-header"] = "_msft-clarity.html"    

    front_matter_dict['post-url'] = f'https://www.meyerperin.com/{filepath.replace(".qmd", ".html")}'
    
    # TODO: if YAML doesn't have repost but cosmos does, need to remove repost from COSMOS

    # In case Cosmos had an update pushing the dates forward because of automatic reposts
    if "twitter-target-date-utc" in cosmos_record\
        and cosmos_record["twitter-target-date-utc"] > cosmos_date_format(convert_to_utc(front_matter_dict["twitter-target-date"]))\
        and "twitter-repost" in cosmos_record and cosmos_record["twitter-repost"] > 0:
        front_matter_dict["twitter-target-date"] = convert_cosmos_utc_to_local(cosmos_record["twitter-target-date-utc"])
    if "linkedin-target-date-utc" in cosmos_record\
        and cosmos_record["linkedin-target-date-utc"] > cosmos_date_format(convert_to_utc(front_matter_dict["linkedin-target-date"]))\
        and "linkedin-repost" in cosmos_record and cosmos_record["linkedin-repost"] > 0:
        front_matter_dict["linkedin-target-date"] = convert_cosmos_utc_to_local(cosmos_record["linkedin-target-date-utc"])

    cosmos_record.update(front_matter_dict)

    # Add the UTC fields to cosmos
    if "twitter-target-date" in front_matter_dict and front_matter_dict["twitter-target-date"]: 
        cosmos_record["twitter-target-date-utc"] = cosmos_date_format(convert_to_utc(front_matter_dict["twitter-target-date"]))

    if "linkedin-target-date" in front_matter_dict and front_matter_dict["linkedin-target-date"]: 
        cosmos_record["linkedin-target-date-utc"] = cosmos_date_format(convert_to_utc(front_matter_dict["linkedin-target-date"]))

    # Add the body to cosmos (since the body is part of the .qmd file but not the YAML front-matter)
    cosmos_record["body"] = txt
    cosmos_record["id"] = id
    cosmos_str = json.dumps(cosmos_record, default=str)
    fixed_cosmos_record = json.loads(cosmos_str)

    front_matter_dict.update(cosmos_record)

    remote_unwanted_fields = ["include-in-header", "twitter-posted", "linkedin-posted", "reset"]
    fixed_cosmos_record = remove_fields_from_dict(fixed_cosmos_record, remote_unwanted_fields)
    cc.upsert_item(fixed_cosmos_record)  
    
    # Remove the body from the front matter (since it's in the .qmd file)
    local_unwanted_fields = [
        "_attachments", "_etag", "_rid", "_self", "_ts", "body", "linkedin-posted-text", "linkedin-posted-utc", 
        "twitter-posted-utc", "twitter-target-date-utc", "linkedin-target-date-utc", "reset"]
    front_matter_dict = remove_fields_from_dict(front_matter_dict, local_unwanted_fields)
    update_front_matter(filepath, front_matter_dict)

def process_directory(di):
    print(f"Processing directory: {di}")
    for root, dirs, files in os.walk(di):
        for filename in files:
            if filename.endswith("qmd"):# and filename > "2022-07":
                filepath = os.path.join(root, filename)
                process_file(filepath)

def main():
    # Takes variables from .env
    load_dotenv()

    # Configure directories with posts
    post_directories = ["posts", "tweets"]

    for di in post_directories:
        process_directory(di)
                    
    return 0

if __name__ == "__main__":
    sys.exit(main())

