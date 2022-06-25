### This is the engine that 
###    - Goes through posts
###    - Determines whether to remove them from draft
###    - Determines whether to post them to LinkedIn and/or Twitter
###    - Posts them to LinkedIn/Twitter

from pydoc import plain
import sys
import os
import pandas as pd
from bs4 import BeautifulSoup
from markdown import markdown
import re
import yaml
import datetime
import requests
import json
from dotenv import load_dotenv
import tweepy
from twilio.rest import Client

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

def linkedin_text(txt, filepath):
    post = txt
    size = len(post)
    if filepath.endswith(".md"):
        linkpath = filepath[:-2] + "html"
    if filepath.endswith(".qmd"):
        linkpath = filepath[:-3] + "html"
    if size > 2900:
        post = post[:2900]
        post += f"""...
        
This post ended up being too long for LinkedIn but the remainder is at https://www.meyerperin.com/{linkpath}

        """
    else:
        post += f"""\n\nThis post originally appeared at https://www.meyerperin.com/{linkpath}"""

    post = post.replace("\n", "\\n")
    post = post.replace('"', '\\"')
    return post

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
        desired_date = fm_date.date()
    elif isinstance(fm_date, datetime.date):
        desired_date = fm_date
    else: # assuming it's a string
        desired_date = datetime.datetime.strptime(fm_date[:10], "%Y-%m-%d").date()

    return desired_date

def main():
    # Takes variables from .env
    load_dotenv()

    # Configure directories with posts
    post_directories = ["posts"]

    # For each directory, process it
    for di in post_directories:
        process_directory(di)
    
    return 0

def get_upload_url(token, person_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    with open("linkedin_upload_asset.json", "r") as f:
        upload_json = f.read()

    upload_json = upload_json.replace("PERSON_URN", person_id)

    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    response = requests.post(url, upload_json, headers=headers)
    response_json = json.loads(response.text)
    upload_url = response_json.get("value").get("uploadMechanism").get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest").get("uploadUrl")
    asset = response_json.get("value").get("asset")

    return asset, upload_url

def upload_image(filepath, upload_url, token):
   headers = {
      "Authorization": f"Bearer {token}"
   }

   resp = requests.put(upload_url, headers=headers, data=open(filepath,'rb').read())
   return resp.status_code

def post_asset(token, person_id, asset, text):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    with open("linkedin_post_image.json", "r") as f:
        post_json = f.read()

    post_json = post_json.replace("PERSON_URN", person_id)
    post_json = post_json.replace("ASSET_URN", asset)
    post_json = post_json.replace("POST_TEXT", text)

    url = "https://api.linkedin.com/v2/ugcPosts"
    resp = requests.post(url, post_json, headers=headers)

    return resp.status_code

def post_to_linkedin(filepath, text, imagepath, front_matter_dict, link=None):

    person_id = os.getenv("LINKEDIN_PERSON_ID")
    token = os.getenv("LINKEDIN_TOKEN")

    li_text = linkedin_text(text, filepath)

    code = 505

    if os.path.exists(imagepath):
        code = post_linkedin_image(li_text, imagepath, person_id, token)
    elif link:
        code = 505
    else:
        # li_text = li_text[:1300]
        code = post_linkedin_text(li_text, person_id, token)

    # if posting was successful, update the front-matter so it won't post again
    if code == 201:
        print(f"\n=====> Posted {filepath} to LinkedIn \n\n")
    else:
        print(f"\n={code}=> Failed to post {filepath} to LinkedIn \n\n")
        

def post_linkedin_text(txt, person_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
   
    with open("linkedin_post_text.json", "r") as f:
        post_json = f.read()

    post_json = post_json.replace("PERSON_URN", person_id)
    post_json = post_json.replace("POST_TEXT", txt)

    print(post_json)

    url = "https://api.linkedin.com/v2/ugcPosts"
    resp = requests.post(url, post_json, headers=headers)

    return resp.status_code

def post_linkedin_image(txt, img_path, person_id, token):
        
    asset, upload_url = get_upload_url(token, person_id)

    resp_code = upload_image(img_path, upload_url, token)
    if resp_code == 201:
        resp_code = post_asset(token, person_id, asset, txt)

    return(resp_code)

def post_twitter_link(txt, link):

    api_key = os.getenv("TWITTER_API_KEY")
    api_key_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACESSS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    # bearer_token  = os.getenv("TWITTER_BEARER_TOKEN")
   
    client = tweepy.Client(consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_token, access_token_secret=access_token_secret)

    response = client.create_tweet(
         text=txt + " " + link,
    )

    return response

def process_file(filepath):
    print(f"Processing {filepath}")
    yml, txt = get_file_plaintext(filepath)

    # For all files, check if we need to adjust the draft field
    front_matter_dict = yaml.safe_load(yml.replace("---", ""))
    
    post_date = get_date(front_matter_dict, "date")
    draft = front_matter_dict.get("draft")
       
    linkedin_posted = get_date(front_matter_dict, "linkedin-posted")
    twitter_posted = get_date(front_matter_dict, "twitter-posted")

    linkedin_repost = front_matter_dict.get("linkedin-repost")
    twitter_repost = front_matter_dict.get("twitter-repost")

    if draft and post_date <= datetime.date.today():
        front_matter_dict["draft"] = False
        draft = False
        print(f"=====> Removed {filepath} from draft")

    if not draft and post_date > datetime.date.today():
        front_matter_dict["draft"] = True
        draft = True
        print(f"=====> Added {filepath} to draft")

    linkedin_target_date = get_date(front_matter_dict, "linkedin-target-date")
    twitter_target_date = get_date(front_matter_dict, "twitter-target-date")

    # Check if I want to move a posting date to the future for LinkedIn
    if linkedin_repost and linkedin_posted and linkedin_target_date < datetime.date.today(): 
        front_matter_dict["linkedin-target-date"] = linkedin_posted + datetime.timedelta(days=linkedin_repost)
        linkedin_target_date = get_date(front_matter_dict, "linkedin-target-date")

    if twitter_repost and twitter_posted and twitter_target_date < datetime.date.today(): 
        front_matter_dict["twitter-target-date"] = twitter_posted + datetime.timedelta(days=twitter_repost)
        twitter_target_date = get_date(front_matter_dict, "twitter-target-date")

    # If target posting date is in the future, remove last posted date
    if linkedin_target_date and linkedin_posted and linkedin_target_date > datetime.date.today():
        front_matter_dict.pop("linkedin-posted")

    if twitter_target_date and twitter_posted and twitter_target_date > datetime.date.today():
        front_matter_dict.pop("twitter-posted")


    # If the article has a "linkedin-target-date" and the article has not been posted to linkedin yet
    # and the article target date is at least today  and the article is not in draft
    if not draft and linkedin_target_date and linkedin_target_date <= datetime.date.today() and not linkedin_posted:
        img = front_matter_dict.get("image")
        linkedin_post_result = post_to_linkedin(filepath, txt, f"/home/lucasmeyer/personal/blog{img}", front_matter_dict)
        linkedin_posted = datetime.date.today().strftime("%Y-%m-%d")
        front_matter_dict["linkedin-posted"] = linkedin_posted
        
        print(f"=====> Posted {filepath} to LinkedIn {linkedin_post_result}")

    if not draft and twitter_target_date and twitter_target_date <= datetime.date.today() and not twitter_posted:
        twitter_text = front_matter_dict.get("twitter-description")
        twitter_url = f"https://www.meyerperin.com/{filepath.replace('.qmd', '.html')}"
        twitter_post_result = post_twitter_link(twitter_text, twitter_url)
        twitter_posted = datetime.date.today().strftime("%Y-%m-%d")
        front_matter_dict["twitter-posted"] = twitter_posted
        print(f"=====> Twitted: https://twitter.com/user/status/{twitter_post_result.data['id']}")

    update_front_matter(filepath, front_matter_dict)

def process_directory(di):
    print(f"Processing directory: {di}")
    calendar = pd.DataFrame(columns=["Target date", "Platform", "Title"])
    for root, dirs, files in os.walk(di):
        for filename in files:
            if filename.endswith("qmd") or filename.endswith("md"):
                filepath = os.path.join(root, filename)
                process_file(filepath)
                calendar = pd.concat([calendar, add_to_calendar(filepath)])
    calendar.sort_values("Target date", inplace=True)
    print(f"Calendar:\n\n{calendar}")

def add_to_calendar(filepath):
    yml, dummy = get_file_plaintext(filepath)
    front_matter_dict = yaml.safe_load(yml.replace("---", ""))

    df = pd.DataFrame(columns=["Target date", "Platform", "Title"])
    tw_date = get_date(front_matter_dict, "twitter-target-date")
    li_date = get_date(front_matter_dict, "linkedin-target-date")
    tw_posted = get_date(front_matter_dict, "twitter-posted")
    li_posted = get_date(front_matter_dict, "linkedin-posted")
    title = front_matter_dict.get("title")


    if tw_date and not tw_posted:
        list = [tw_date.strftime("%Y-%m-%d"), "Twitter", title]
        df = pd.concat([df, pd.DataFrame([list], columns=["Target date", "Platform", "Title"])])
    if li_date and not li_posted:
        list = [li_date.strftime("%Y-%m-%d"), "LinkedIn", title]
        df = pd.concat([df, pd.DataFrame([list], columns=["Target date", "Platform", "Title"])])
    
    return df

if __name__ == "__main__":
    sys.exit(main())
