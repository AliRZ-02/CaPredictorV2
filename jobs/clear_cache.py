import os
import requests

if __name__ == "__main__":
    url = os.getenv("API_URL", "")

    if url:
        ret = requests.get(f'{url}/clear_cache')