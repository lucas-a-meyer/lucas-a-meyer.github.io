git pull
source /home/lucasmeyer/personal/blog/.venv/bin/activate
/usr/bin/python3 -m pip install -r /home/lucasmeyer/personal/blog/requirements.txt
quarto render
/usr/bin/python3 /home/lucasmeyer/personal/twilio/rendered.py
deactivate
