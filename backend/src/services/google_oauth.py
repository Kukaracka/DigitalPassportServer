import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()

oauth = OAuth()

cid = os.getenv("GOOGLE_CLIENT_ID")
cscr = os.getenv("GOOGLE_CLIENT_SECRET")

oauth.register(
    name='google',
    client_id=cid,
    client_secret=cscr,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
