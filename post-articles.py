### This is the engine that 
###    - Goes through posts
###    - Determines whether to remove them from draft
###    - Determines whether to post them to LinkedIn and/or Twitter
###    - Posts them to LinkedIn/Twitter

from pydoc import plain
import sys
import os
from bs4 import BeautifulSoup
from markdown import markdown
import re
import yaml
import datetime
from distutils.command.upload import upload
import requests
import json

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

def linkedin_text(txt):
    post = txt
    size = len(post)
    if size > 2800:
        post = post[:2800]
        post += """...
        
(Sorry...this post ended up being too big for LinkedIn. The complete post is in my blog, at www(dot)meyerperin(dot)com .)

        """
    else:
        post += """\n\nI posted this automatically from my blog using my Quarto to Linkedin converter. You can see my older posts and more at my blog, at www(dot)meyerperin(dot)com ."""

    post = post.replace("\n", "\\n")
    post = post.replace('"', '\\"')
    return post


def ensure_future_posts_is_draft(filepath, yml, front_matter):
    
    front_matter["draft"] = True
    # If the file has a linkedin field, adjust the text 
    # and check if I should post
    with open(filepath, "r") as f:
        md_content = f.read()
    
    new_yml = yaml.dump(front_matter)
    new_yml = f"---\n{new_yml}---"
    md_content = md_content.replace(yml, new_yml)
    with open(filepath, "w") as f:
        f.write(md_content)

def remove_draft(filepath, yml, front_matter):
    
    front_matter["draft"] = False
    # If the file has a linkedin field, adjust the text 
    # and check if I should post
    with open(filepath, "r") as f:
        md_content = f.read()
    
    new_yml = yaml.dump(front_matter)
    new_yml = f"---\n{new_yml}---"
    md_content = md_content.replace(yml, new_yml)
    with open(filepath, "w") as f:
        f.write(md_content)



def get_date(front_matter, field):
    fm_date = front_matter.get(field)
    if not fm_date:
        return None

    if isinstance(fm_date, datetime.datetime) or isinstance(fm_date, datetime.date):
        desired_date = fm_date.date()
    else:
        desired_date = datetime.datetime.strptime(fm_date[:10], "%Y-%m-%d").date()

    return desired_date

def process_directory(di):
    print(f"Processing directory: {di}")
    for root, dirs, files in os.walk(di):
        for filename in files:
            if filename.endswith("qmd") or filename.endswith("md"):
                filepath = os.path.join(root, filename)
                process_file(filepath)

def main():
    post_directories = ["posts"]

    for di in post_directories:
        process_directory(di)
    return 0

def get_upload_url(token, person_id):

   headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
   }

   upload_json = """
   {
      "registerUploadRequest": {
         "recipes": [
               "urn:li:digitalmediaRecipe:feedshare-image"
         ],
         "owner": "PERSON_URN",
         "serviceRelationships": [
               {
                  "relationshipType": "OWNER",
                  "identifier": "urn:li:userGeneratedContent"
               }
         ]
      }
   }
   """

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

   post_json = """
   {
      "author": "PERSON_URN",
      "lifecycleState": "PUBLISHED",
      "specificContent": {
         "com.linkedin.ugc.ShareContent": {
               "shareCommentary": {
                  "text": "POST_TEXT"
               },
               "shareMediaCategory": "IMAGE",
               "media": [
                  {
                     "status": "READY",
                     "description": {
                           "text": "Center stage!"
                     },
                     "media": "ASSET_URN",
                     "title": {
                           "text": "Where does the title go?"
                     }
                  }
               ]
         }
      },
      "visibility": {
         "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
      }
   }
   """

   post_json = post_json.replace("PERSON_URN", person_id)
   post_json = post_json.replace("ASSET_URN", asset)
   post_json = post_json.replace("POST_TEXT", text)

   url = "https://api.linkedin.com/v2/ugcPosts"
   resp = requests.post(url, post_json, headers=headers)

   return resp.status_code

def post_to_linkedin(filepath, text, imagepath, front_matter, yml, link=None):

    cfg_file = open("/home/lucasmeyer/.linkedin/config.json")
    li_cfg = json.load(cfg_file)

    person_id = li_cfg.get("urn")
    token = li_cfg.get("access_token")

    li_text = linkedin_text(text)

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
        front_matter["posted-to-linkedin"] = datetime.date.today().strftime("%Y-%m-%d")
        with open(filepath, "r") as f:
            md_content = f.read()
        
        new_yml = yaml.dump(front_matter)
        new_yml = f"---\n{new_yml}---"
        md_content = md_content.replace(yml, new_yml)
        with open(filepath, "w") as f:
            f.write(md_content) 
            print(f"\n==================> Posted {filepath} to LinkedIn \n\n")
    else:
            print(f"\n====={code}==========> Failed to post {filepath} to LinkedIn \n\n")
        

def post_linkedin_text(txt, person_id, token):
   headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
   }

   post_json = """
   {
        "author": "PERSON_URN",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "POST_TEXT"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
   """

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

def process_file(filepath):
    # print(f"Processing {filepath}")
    yml, txt = get_file_plaintext(filepath)

    # For all files, check if we need to adjust the draft field
    front_matter = yaml.safe_load(yml.replace("---", ""))
    post_date = get_date(front_matter, "date")
    draft = front_matter.get("draft")

    if draft and post_date <= datetime.date.today():
        remove_draft(filepath, yml, front_matter)
        print(f"==========> Removed {filepath} from draft")

    if not draft and post_date > datetime.date.today():
        ensure_future_posts_is_draft(filepath, yml, front_matter)   
        print(f"==========> Added {filepath} to draft")

    li_post_date = get_date(front_matter, "linkedin-target-date")
    last_li_post = get_date(front_matter, "posted-to-linkedin")
    
    # If the article has a "linkedin-target-date"
    # and the article has not been posted to linkedin yet
    # and the article target date is at least today
    if li_post_date and not last_li_post and li_post_date <= datetime.date.today():
        img = front_matter.get("image")
        post_to_linkedin(filepath, txt, f"/home/lucasmeyer/personal/blog{img}", front_matter, yml)

    # If the file has a linkedin field, adjust the text 
    # and check if I should post


if __name__ == "__main__":
    sys.exit(main())
