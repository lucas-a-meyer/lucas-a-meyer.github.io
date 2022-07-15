import os

posts_dir = "docs/posts"
for root, dirs, files in os.walk(posts_dir):
    for name in files:
        target = os.path.join(root, name)
        target = target[len(posts_dir):]
        print(target)