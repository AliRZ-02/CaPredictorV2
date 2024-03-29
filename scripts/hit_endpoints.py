import os
import logging
import requests

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

def hit_frontend_endpoint():
    res = requests.get(f"{FRONTEND_URL}")

    if not res.status_code == 200:
        logger.warning(f"Couldn't reach Frontend: Status {res.status_code}")

def hit_backend_endpoint():
    res = requests.get(f"{BACKEND_URL}/player/1")

    if not res.status_code == 404:
        logger.warning(f"Couldn't reach Backend: Status {res.status_code}")

if __name__ == "__main__":
    hit_frontend_endpoint()
    hit_backend_endpoint()
