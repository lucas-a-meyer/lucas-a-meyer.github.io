cd /home/lucasmeyer/personal/blog/
git pull
/home/lucasmeyer/personal/blog/.venv/bin/activate
/usr/bin/python3 -m pip install -r /home/lucasmeyer/personal/blog/requirements.txt
/usr/local/bin/quarto render
/usr/bin/python3 /home/lucasmeyer/personal/twilio/rendered.py
