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
    if size > 3000:
        post = post[:3000]
        post += """...
        
(Sorry...this post ended up being too big for LinkedIn. The complete post is in my blog, at www[dot]meyerperin[dot]com.)

        """
    else:
        post += """\n\nYou can see my older posts and more at my blog, at www[dot]meyerperin[dot]com."""
    return post

def post_to_linkedin(title, text, imagepath):
    li_text = linkedin_text(text)
    print(f"\n======= {title} ({len(text)}) =======\n\n")
    print(f"Image: {imagepath}")
    print()
    print(li_text)
    print(f"\n==============\n\n")

def process_file(filepath):
    print(f"Processing {filepath}")
    yml, txt = get_file_plaintext(filepath)

    # For all files, check if we need to adjust the draft field
    front_matter = yaml.safe_load(yml.replace("---", ""))
    post_date = datetime.datetime.strptime(front_matter.get("date"), "%Y-%m-%d").date()
    
    if post_date > datetime.date.today():
        front_matter["draft"] = True
        # If the file has a linkedin field, adjust the text 
        # and check if I should post
        with open(filepath) as f:
            
        

        img = ""
        print(front_matter)
        post_to_linkedin(filepath, txt, img)


    # If the file has a linkedin field, adjust the text 
    # and check if I should post



def generate_plaintext_for_directory(di):
    print(f"Files and directories for {di}")
    for root, dirs, files in os.walk(di):
        for filename in files:
            if filename.endswith("qmd") or filename.endswith("md"):
                filepath = os.path.join(root, filename)
                process_file(filepath)

def main():
    post_directories = ["posts"]

    for di in post_directories:
        generate_plaintext_for_directory(di)
    return 0



if __name__ == "__main__":
    sys.exit(main())
