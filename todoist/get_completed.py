import json
import requests
from urllib.parse import urljoin
from typing import Dict
import configparser
import pandas as pd
from datetime import datetime
from datetime import timezone


BASE_URL = "https://api.todoist.com"
AUTH_BASE_URL = "https://todoist.com"
SYNC_VERSION = "v9"
SYNC_API = urljoin(BASE_URL, f"/sync/{SYNC_VERSION}/")
AUTHORIZATION = ("Authorization", "Bearer %s")


def create_headers(token: str) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    headers.update([(AUTHORIZATION[0], AUTHORIZATION[1] % token)])
    return headers


def get_sync_url(relative_path: str) -> str:
    return urljoin(SYNC_API, relative_path)


def request_string(request_string: str, **kwargs) -> str:
    end_point = get_sync_url(request_string)
    filters = "".join(f"&{k}={v}" for k, v in kwargs.items())
    return f"{end_point}?{filters}"


def get_request(url: str, header: str) -> json:
    try:
        r = requests.get(url, headers=header)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return r.json()


def date_offset(date_input: datetime, week_num: int, week_day: int) -> datetime:
    date = date_input + pd.tseries.offsets.Week(week_num, weekday=week_day)
    return date


def format_str(date: datetime, strformat: str) -> str:
    return date.strftime(strformat)


def json_to_df(json: json, path: list) -> pd.DataFrame():
    return pd.json_normalize(json, record_path=path)


def timezone_to_utc(date: datetime) -> str:
    return date.tz_convert(timezone.utc).strftime("%Y-%m-%dT%H:%M")


def main():

    config = configparser.ConfigParser()

    config.read("settings.ini")

    request_header = create_headers(config["API_CONFIG"]["API_CODE"])

    get_timezone_url = get_sync_url("user")

    get_timezone_request = get_request(url=get_timezone_url, header=request_header)

    timezone = get_timezone_request["tz_info"]["timezone"]

    date_today = datetime.now().date()

    mon_week_adj = -2 if date_today.weekday() != 0 else -1

    prev_monday = date_offset(
        date_input=date_today, week_num=mon_week_adj, week_day=0
    ).tz_localize(timezone)

    prev_sunday = date_offset(
        date_input=date_today, week_num=-1, week_day=6
    ).tz_localize(timezone)

    get_completed_url = request_string(
        "completed/get_all", since=timezone_to_utc(prev_monday), until=timezone_to_utc(prev_sunday)
    )

    get_completed_request = get_request(url=get_completed_url, header=request_header)

    df_items = json_to_df(get_completed_request, ["items"])

    df_items.assign(
        completed_at=pd.to_datetime(df_items["completed_at"])
        .dt.tz_convert(timezone)
        .dt.strftime("%Y-%m-%d %H:%M")
    ).to_csv(f"completedItems_{prev_sunday.date()}.csv", index=False)


if __name__ == "__main__":
    main()
