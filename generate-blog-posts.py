import pandas as pd
import os


def toKebab(s):
    r=""
    lower_s = s.lower()
    for c in lower_s:
        if c.isalnum():
            r += c
        elif c == " ":
            r += "-"
    return r

def generateFileName(date, title, format):
    date_part = date.strftime("%Y-%m-%d")
    title_part = toKebab(title)
    format_part = format
    return f"{date_part}-{title_part}.{format_part}"

def generateFileContent(date, title, tags, embed):
    fileContent = f"""---
layout: post
title: "{title}"
date: {date} 12:00 -0400
categories: {tags}
---
{embed}
"""
    return fileContent

def generatePosts(directory, postsListFile):
    df = pd.read_excel(postsListFile)
    for i, r in df.iterrows():
        fileName = generateFileName(r['Date'], r['Title'], "md")
        fileContent = generateFileContent(r['Date'].strftime("%Y-%m-%d"), r['Title'], r['Tags'], r['Embed link'])
        with open(os.path.join(directory, fileName), 'w') as fp:
            fp.write(fileContent)

generatePosts("_posts", "posts.xlsx")

