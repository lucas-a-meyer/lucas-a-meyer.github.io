import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_ID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Find these values at https://twilio.com/user/account
# To set up environmental variables, see http://twil.io/secure

client = Client(account_sid, auth_token)

client.api.account.messages.create(
    to="+14258776991",
    from_="+19783965634",
    body="Blog rendered!"
)

