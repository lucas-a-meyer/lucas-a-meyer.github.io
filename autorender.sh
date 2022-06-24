cd /home/lucasmeyer/personal/blog/
git stash --include-untracked
git pull
/home/lucasmeyer/personal/blog/.venv/bin/activate
/usr/bin/python3 -m pip install -r /home/lucasmeyer/personal/blog/requirements.txt --quiet
/usr/local/bin/quarto render
/usr/bin/python3 /home/lucasmeyer/personal/blog/text_blog_rendered.py
