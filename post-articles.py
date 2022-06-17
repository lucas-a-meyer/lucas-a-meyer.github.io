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

def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    markdown_string = re.sub(r"```.*?```", '', markdown_string, 0, re.DOTALL)
    markdown_string = re.sub(r"---.*?---", '', markdown_string, 0, re.DOTALL)
    
    markdown_string = '\n'.join([i for i in markdown_string.splitlines() if not i.startswith("#")])

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    html = re.sub(r'<li>(.*?)</li>', r'- \g<1>', html)
    # Remove Quarto markdown options
    html = re.sub(r'{(.*?)}', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return text

def main():
    post_directories = ["posts"]

    for di in post_directories:
        print(f"Files and directories for {di}")
        for root, dirs, files in os.walk(di):
            for filename in files:
                if filename.endswith("qmd") or filename.endswith("md"):
                    filepath = os.path.join(root, filename)
                    print(filepath)
                    with open(filepath) as f:
                        print(markdown_to_text(f.read()))

    return 0


if __name__ == "__main__":
    sys.exit(main())
