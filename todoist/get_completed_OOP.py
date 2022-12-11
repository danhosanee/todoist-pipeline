import json
import requests
from urllib.parse import urljoin
from typing import Dict
import configparser
import pandas as pd
from datetime import datetime
from datetime import timezone
from dataclasses import dataclass

BASE_URL = "https://api.todoist.com"
AUTH_BASE_URL = "https://todoist.com"
SYNC_VERSION = "v9"
SYNC_API = urljoin(BASE_URL, f"/sync/{SYNC_VERSION}/")
AUTHORIZATION = ("Authorization", "Bearer %s")


@dataclass
class TodoistCompleted:
    token : str

    def create_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        headers.update([(AUTHORIZATION[0], AUTHORIZATION[1] % self.token)])
        return headers

    def get_sync_url(self, relative_path : str) -> str:
        return urljoin(SYNC_API, relative_path)

    def request_string(self, request_string : str , **kwargs) -> str:
        end_point = self.get_sync_url(request_string)
        filters = "".join(f"&{k}={v}" for k, v in kwargs.items())
        return f"{end_point}?{filters}" 

@dataclass
class API:
    header: TodoistCompleted.create_headers()
    url : TodoistCompleted.request_string()

    def get_request(self) -> json:
        try:
            r = requests.get(self.url, headers=self.header)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return r.json()





def main():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    todoist = TodoistCompleted(config["API_CONFIG"]["API_CODE"])

    todoist.request_string("completed/get_all", since="2021-10-01")

    api = API()
    print(api)
    


if __name__ == "__main__":
    main()