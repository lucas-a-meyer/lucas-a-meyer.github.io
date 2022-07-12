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

def update_lucas(body):

    account_sid = os.getenv("TWILIO_ACCOUNT_ID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(
        to="+14258776991",
        from_="+19783965634",
        body=body
    )

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
    html = re.sub(r'\$\$(.*?)\$\$', r'\g<1>', html)

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

def get_date(front_matter_dict, field):
    fm_date = front_matter_dict.get(field)
    
    if not fm_date:
        return None

    if isinstance(fm_date, datetime.datetime):
        desired_date = fm_date
    elif isinstance(fm_date, datetime.date):
        desired_date = datetime.datetime.combine(fm_date, datetime.datetime.min.time()) + datetime.timedelta(hours=6)
    else: # assuming it's a string
        desired_date = datetime.datetime.strptime(fm_date[:10], "%Y-%m-%d").date()
        desired_date = datetime.datetime.combine(desired_date, datetime.datetime.min.time()) + datetime.timedelta(hours=6)

    return desired_date

def convert_to_utc(local_time: datetime.datetime) -> datetime: 
    ts = datetime.datetime.timestamp(local_time)
    return datetime.datetime.utcfromtimestamp(ts)

def cosmos_date_format(dt: datetime.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H-%M-%S.%f0Z")

def my_cosmos_client(db, container):
    COSMOS_URI = os.environ["COSMOS_URI"]
    COSMOS_KEY = os.environ["COSMOS_KEY"]

    client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
    database = client.get_database_client(db)
    return database.get_container_client(container)
    
def queue_twitter_post(target_time_local: datetime.datetime, text: str, link:str = None, image_url:str = None, repeat:int = None):

    cc = my_cosmos_client("social-media", "tweets")
    now = datetime.datetime.now()

    target_time_utc = cosmos_date_format(convert_to_utc(target_time_local))
    id = (f"{target_time_local.strftime('%Y-%m-%d-%H-%M-%S')}-{now.strftime('%Y-%m-%d-%H-%M-%S-%f')}")
    
    if link:
        text = text + " " + link

    record = {
        "id": id,
        "body": text,
        "twitter_target_date_utc": target_time_utc
    }

    if image_url:
        record['image_url'] = image_url   
    if repeat:
        record['repeat'] = repeat

    cc.upsert_item(record)

def queue_linkedin_post(filepath: str, text, img_path, front_matter_dict, linkedin_linkback):
    print("Queueing LinkedIn post")

    post_url = f'https://www.meyerperin.com/{filepath.replace(".qmd", ".html")}'

    cc = my_cosmos_client("social-media", "linkedin_posts")
    now = datetime.datetime.now()

    target_time_utc = cosmos_date_format(convert_to_utc(front_matter_dict["linkedin-target-date"]))
    id = f'{front_matter_dict["linkedin-target-date"].strftime("%Y-%m-%d-%H-%M-%S")}-{now.strftime("%Y-%m-%d-%H-%M-%S-%f")}'
    
    record = {
        "id": id,
        "body": text,
        "image_url": img_path,
        "linkedin_target_date_utc": target_time_utc,
        "linkback": linkedin_linkback,
        "post_url": post_url
    }

    cc.upsert_item(record)

def process_file(filepath):
    print(f"Processing {filepath}")
    yml, txt = get_file_plaintext(filepath)

    # For all files, check if we need to adjust the draft field
    front_matter_dict = yaml.safe_load(yml.replace("---", ""))
    
    post_date = get_date(front_matter_dict, "date")
    draft = front_matter_dict.get("draft")

    if post_date:       
        if draft and post_date <= datetime.datetime.now():
            front_matter_dict["draft"] = False
            draft = False
            update_lucas(f"Removed {filepath} from draft")

        if not draft and post_date > datetime.datetime.now():
            front_matter_dict["draft"] = True
            draft = True
            update_lucas(f"Added {filepath} to draft")

    linkedin_posted = get_date(front_matter_dict, "linkedin-posted")
    twitter_posted = get_date(front_matter_dict, "twitter-posted")

    linkedin_repost = front_matter_dict.get("linkedin-repost")
    twitter_repost = front_matter_dict.get("twitter-repost")
    
    linkedin_target_date = get_date(front_matter_dict, "linkedin-target-date")
    twitter_target_date = get_date(front_matter_dict, "twitter-target-date")

    linkedin_linkback = front_matter_dict.get("linkedin-linkback")

    # Check if I want to move a posting date to the future for LinkedIn
    if linkedin_repost and linkedin_posted and linkedin_target_date < datetime.datetime.now(): 
        front_matter_dict["linkedin-target-date"] = linkedin_posted + datetime.timedelta(days=linkedin_repost)
        linkedin_target_date = get_date(front_matter_dict, "linkedin-target-date")
    if twitter_repost and twitter_posted and twitter_target_date < datetime.datetime.now(): 
        front_matter_dict["twitter-target-date"] = twitter_posted + datetime.timedelta(days=twitter_repost)
        twitter_target_date = get_date(front_matter_dict, "twitter-target-date")

    # If target posting date is in the future, remove last posted date
    if linkedin_target_date and linkedin_posted and linkedin_target_date > datetime.datetime.now():
        front_matter_dict.pop("linkedin-posted")
    if twitter_target_date and twitter_posted and twitter_target_date > datetime.datetime.now():
        front_matter_dict.pop("twitter-posted")

    # If the article has a "linkedin-target-date" and the article has not been posted to linkedin yet
    # and the article target date is at least today  and the article is not in draft
    if linkedin_target_date and not linkedin_posted: # and not draft
        img = front_matter_dict.get("image")
        # post_to_linkedin(filepath, txt, img, front_matter_dict, linkedin_linkback)
        queue_linkedin_post(filepath, txt, img, front_matter_dict, linkedin_linkback)
        linkedin_posted = datetime.datetime.now()
        front_matter_dict["linkedin-posted"] = linkedin_posted

    if not draft and twitter_target_date and not twitter_posted:
        post_type = front_matter_dict.get("post-type")
        twitter_text = ""
        if front_matter_dict.get("twitter-description"):
            twitter_text = front_matter_dict.get("twitter-description")
        else: # doesn't have a description, let's get it from the text
            last_break = txt[:240].rfind("\\n")
            if last_break == -1:
                last_break = 240            
                twitter_text = txt[:last_break]       
        if not post_type or post_type == "link":
            twitter_url = f"https://www.meyerperin.com/{filepath.replace('.qmd', '.html')}"
            queue_twitter_post(twitter_target_date, twitter_text, twitter_url)
            twitter_posted = datetime.datetime.now()
        if post_type == "text":
            print(f"Gonna tweet: {twitter_text}")
            queue_twitter_post(twitter_target_date, twitter_text)
            twitter_posted = datetime.datetime.now()
        front_matter_dict["twitter-posted"] = twitter_posted

    # Check that we have Microsoft Clarity installed in the page
    if not front_matter_dict.get("include-in-header"):
        front_matter_dict["include-in-header"] = "_msft-clarity.html"

    if post_date: front_matter_dict["date"] = post_date
    if linkedin_posted: front_matter_dict["linkedin-posted"] = linkedin_posted
    if twitter_posted: front_matter_dict["twitter-posted"] = twitter_posted
    if linkedin_target_date: front_matter_dict["linkedin-target-date"] = linkedin_target_date
    if twitter_target_date: front_matter_dict["twitter-target-date"] = twitter_target_date
    
    update_front_matter(filepath, front_matter_dict)

def process_directory(di):
    print(f"Processing directory: {di}")
    for root, dirs, files in os.walk(di):
        for filename in files:
            if filename.endswith("qmd") or filename.endswith("md"):
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

