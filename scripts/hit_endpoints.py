import os
import logging
import requests

logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL")
BACKEND_URL = os.getenv("BACKEND_URL")

def hit_frontend_endpoint():
    try:
        requests.get(f"{FRONTEND_URL}", timeout=0.5)
    except:
        pass

def hit_backend_endpoint():
    try:
        requests.get(f"{BACKEND_URL}/player/1", timeout=0.5)
    except:
        pass

if __name__ == "__main__":
    hit_frontend_endpoint()
    hit_backend_endpoint()
