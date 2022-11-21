import json
import requests
from urllib.parse import urljoin
from typing import Dict
import pandas as pd
from datetime import datetime
from datetime import timezone
import os
import boto3
from io import StringIO

BASE_URL = "https://api.todoist.com"
AUTH_BASE_URL = "https://todoist.com"
SYNC_VERSION = "v9"
SYNC_API = urljoin(BASE_URL, f"/sync/{SYNC_VERSION}/")
AUTHORIZATION = ("Authorization", "Bearer %s")
AWS_S3_BUCKET = "todoist-completed"


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


def tz_to_utc(date: datetime) -> str:
    return date.tz_convert(timezone.utc).strftime("%Y-%m-%dT%H:%M")


def lambda_handler(event, context):

    request_header = create_headers(os.environ["API_CODE"])

    get_tz_url = get_sync_url("user")

    get_tz_request = get_request(url=get_tz_url, header=request_header)

    tz = get_tz_request["tz_info"]["timezone"]

    date_today = datetime.now().date()

    mon_week_adj = -2 if date_today.weekday() != 0 else -1

    prev_monday = date_offset(
        date_input=date_today, week_num=mon_week_adj, week_day=0
    ).tz_localize(tz)

    prev_sunday = date_offset(
        date_input=date_today, week_num=-1, week_day=6
    ).tz_localize(tz)

    get_completed_url = request_string(
        "completed/get_all", since=tz_to_utc(prev_monday), until=tz_to_utc(prev_sunday)
    )

    get_completed_request = get_request(url=get_completed_url, header=request_header)

    df_items = json_to_df(get_completed_request, ["items"])

    csv_buffer = StringIO()

    df_items.assign(
        completed_at=pd.to_datetime(df_items["completed_at"]).dt.tz_convert(tz)
    ).to_csv(csv_buffer, index=False)

    s3_resource = boto3.resource("s3")

    s3_resource.Object(AWS_S3_BUCKET, f"completedItems_{prev_sunday.date()}.csv").put(
        Body=csv_buffer.getvalue()
    )

    return {"status_code": 200}


if __name__ == "__main__":
    lambda_handler()
