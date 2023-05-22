import yaml
import datetime

def check_header(article_yaml_header: str) -> bool:
    # load the yaml from article_yaml
    dict_header = yaml.load(article_yaml_header, Loader=yaml.FullLoader)

    # check that it has the required fields
    if "author" not in dict_header or dict_header["author"] == "":
        print("'author' is missing")
        return False

    if "date" not in dict_header:
        print("'date' is missing")
        return False
    
    # check that dict_header_date is of type datetime.datetime
    if type(dict_header["date"]) != datetime.datetime:
        print(f"'date' is not a datetime, it's {type(dict_header['date'])}")
        return False

    # check that dict_header_image is not empty
    if "image" not in dict_header or dict_header["image"] == "":
        print("Image is missing or empty")
        return False

    if "draft" not in dict_header:
        print("'draft' is missing")
        return False
        
    # check that dict_header_draft is of type boolean
    if type(dict_header['draft']) != bool:
        print("'draft' is not a boolean")
        return False
    
    # check that dict_header_clarity is equal to _msft-clarity.html
    if "include-in-header" not in dict_header or dict_header["include-in-header"] != "_msft-clarity.html":
        print("'include-in-header' is not equal to _msft-clarity.html")
        return False
    
    # check that dict_header_title is not empty
    if "title" not in dict_header or dict_header["title"] == "":
        print("'title' is missing empty")
        return False

    return True

    # required

def create_header(title, date, image_file_name) -> str:
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
    
def update_header_dates(staged_header: dict) -> dict:
    # TODO: check header

    blog_date = staged_header["date"]

    # generate a twitter-target-date with the same date as the blog_date, but 7:01:00 AM
    twitter_target_date = blog_date.replace(hour=7, minute=1, second=0)
    linkedin_target_date = blog_date.replace(hour=7, minute=1, second=0)

    staged_header["twitter-target-date"] = twitter_target_date
    staged_header["linkedin-target-date"] = linkedin_target_date

    return staged_header



if __name__ == '__main__':
    article_yaml_header = """
author: Lucas A. Meyer
categories:
- technology
- cautionary tales
date: 2022-12-08 06:00:00
draft: false
id: 19ff589a2eb2c55d79a8225a00891454
image: https://mpsocial.blob.core.windows.net/blog-images/mizuho-post.jpg
include-in-header: _msft-clarity.html
linkedin-target-date: 2022-12-08 08:00:00
linkedin-url: https://www.linkedin.com/embed/feed/update/urn:li:share:7006648606996783104
post-url: https://www.meyerperin.com/posts/2022-12-08-mizuho-securities.html
title: The data entry error that cost hundreds of millions
tweet-url: https://twitter.com/user/status/1600882904434876417
twitter-target-date: 2022-12-08 08:00:00
    """

    if check_header(article_yaml_header):
        print("Header is valid")
    else:
        print("Header is invalid")
    




    

    

    

    #### check that it has the required fields

    #### required
    # author
    # date
    # draft
    # image
    # clarity
    # title
    # draft

    ##### optional 
    # twitter-target-date
    # linkedin-target-date
    # categories

    #### must not have
    # Stuff that appears after posting
    # id
    # linkedin-posted
    # linkedin-url
    # post-url
    # twitter-posted
    # tweet-url




