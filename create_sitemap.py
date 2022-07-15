import os

posts_dir = "docs/posts"
site_root = "https://www.meyerperin.com/posts/"
for root, dirs, files in os.walk(posts_dir):
    for name in files:
        target = os.path.join(root, name)
        target = f"{site_root}{target[len(posts_dir):]}"
        print(target)