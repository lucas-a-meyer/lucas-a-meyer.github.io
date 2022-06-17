### This is the engine that 
###    - Goes through posts
###    - Determines whether to remove them from draft
###    - Determines whether to post them to LinkedIn and/or Twitter
###    - Posts them to LinkedIn/Twitter
import sys
import os

def main():
    post_directories = ["posts"]

    for di in post_directories:
        print(f"Files and directories for {di}")
        for root, dirs, files in os.walk(di):
            for f in files:
                if f.endswith("qmd") or f.endswith("md"):
                    print(os.path.join(root, f))

    return 0


if __name__ == "__main__":
    sys.exit(main())
