
import os

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests


def verify_google_token(token):
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    payload = google_id_token.verify_oauth2_token(
        token, google_requests.Request(), client_id
    )
    return payload
