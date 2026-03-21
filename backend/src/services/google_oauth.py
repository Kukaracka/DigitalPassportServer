from authlib.integrations.starlette_client import OAuth
from core.config import get_settings


oauth = OAuth()
settings = get_settings()

cid = settings.CID
cscr = settings.CSCR

oauth.register(
    name="google",
    client_id=cid,
    client_secret=cscr,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
